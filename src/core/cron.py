# src/core/cron.py
"""
Cron job management for Hermes Toolkit.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class CronJob:
    """Represents a scheduled cron job."""

    def __init__(
        self,
        name: str,
        prompt: str,
        schedule: str,
        job_id: Optional[str] = None,
        deliver: str = 'origin',
        skills: Optional[List[str]] = None,
        model: Optional[Dict[str, str]] = None,
        status: str = 'active',
        created_at: Optional[str] = None,
        last_run: Optional[str] = None,
        next_run: Optional[str] = None,
    ):
        self.job_id = job_id or str(uuid.uuid4())
        self.name = name
        self.prompt = prompt
        self.schedule = schedule
        self.deliver = deliver
        self.skills = skills or []
        self.model = model or {'provider': '', 'model': ''}
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.last_run = last_run
        self.next_run = next_run

    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'name': self.name,
            'prompt': self.prompt,
            'schedule': self.schedule,
            'deliver': self.deliver,
            'skills': self.skills,
            'model': self.model,
            'status': self.status,
            'created_at': self.created_at,
            'last_run': self.last_run,
            'next_run': self.next_run,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CronJob':
        return cls(
            name=data.get('name', ''),
            prompt=data.get('prompt', ''),
            schedule=data.get('schedule', ''),
            job_id=data.get('job_id'),
            deliver=data.get('deliver', 'origin'),
            skills=data.get('skills', []),
            model=data.get('model', {'provider': '', 'model': ''}),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            last_run=data.get('last_run'),
            next_run=data.get('next_run'),
        )


class CronLog:
    """Represents a cron job execution log."""

    def __init__(
        self,
        job_id: str,
        log_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        success: bool = True,
        output: str = '',
        error: str = '',
    ):
        self.log_id = log_id or str(uuid.uuid4())
        self.job_id = job_id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            'log_id': self.log_id,
            'job_id': self.job_id,
            'timestamp': self.timestamp,
            'success': self.success,
            'output': self.output,
            'error': self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CronLog':
        return cls(
            job_id=data.get('job_id', ''),
            log_id=data.get('log_id'),
            timestamp=data.get('timestamp'),
            success=data.get('success', True),
            output=data.get('output', ''),
            error=data.get('error', ''),
        )


class CronManager:
    """
    Manages scheduled cron jobs for Hermes Toolkit.
    """

    def __init__(self, cron_file: Optional[str] = None, logs_dir: Optional[str] = None):
        if cron_file:
            self._cron_file = Path(cron_file)
        else:
            self._cron_file = Path.home() / '.hermes' / 'crontab.json'

        if logs_dir:
            self._logs_dir = Path(logs_dir)
        else:
            self._logs_dir = Path.home() / '.hermes' / 'cron_logs'

        self._cron_file.parent.mkdir(parents=True, exist_ok=True)
        self._logs_dir.mkdir(parents=True, exist_ok=True)

        self._jobs: List[CronJob] = []
        self._load_jobs()

    def _load_jobs(self) -> None:
        """Load cron jobs from file."""
        self._jobs = []
        if self._cron_file.exists():
            try:
                with open(self._cron_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    jobs_data = data if isinstance(data, list) else data.get('jobs', [])
                    self._jobs = [CronJob.from_dict(j) for j in jobs_data]
            except (json.JSONDecodeError, IOError):
                self._jobs = []

    def _save_jobs(self) -> bool:
        """Save cron jobs to file."""
        try:
            data = {
                'jobs': [j.to_dict() for j in self._jobs],
                'updated_at': datetime.now().isoformat(),
            }
            with open(self._cron_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def list_jobs(self, status: Optional[str] = None) -> List[CronJob]:
        """
        List all cron jobs, optionally filtered by status.

        Args:
            status: Filter by 'active' or 'paused', or None for all

        Returns:
            List of CronJob objects
        """
        if status:
            return [j for j in self._jobs if j.status == status]
        return self._jobs.copy()

    def get_job(self, job_id: str) -> Optional[CronJob]:
        """Get a specific cron job by ID."""
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None

    def create_job(
        self,
        name: str,
        prompt: str,
        schedule: str,
        deliver: str = 'origin',
        skills: Optional[List[str]] = None,
        model: Optional[Dict[str, str]] = None,
    ) -> Optional[CronJob]:
        """Create a new cron job."""
        job = CronJob(
            name=name,
            prompt=prompt,
            schedule=schedule,
            deliver=deliver,
            skills=skills,
            model=model,
        )
        self._jobs.append(job)
        if self._save_jobs():
            return job
        self._jobs.remove(job)
        return None

    def update_job(self, job_id: str, **kwargs) -> bool:
        """Update an existing cron job."""
        job = self.get_job(job_id)
        if not job:
            return False

        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        if self._save_jobs():
            return True
        return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a cron job."""
        job = self.get_job(job_id)
        if not job:
            return False

        self._jobs.remove(job)
        if self._save_jobs():
            return True
        self._jobs.append(job)
        return False

    def pause_job(self, job_id: str) -> bool:
        """Pause a cron job."""
        return self.update_job(job_id, status='paused')

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused cron job."""
        return self.update_job(job_id, status='active')

    def get_job_logs(self, job_id: str, limit: int = 50) -> List[CronLog]:
        """Get execution logs for a cron job."""
        logs = []
        log_file = self._logs_dir / f'{job_id}.json'

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logs = [CronLog.from_dict(l) for l in data[-limit:]]
            except (json.JSONDecodeError, IOError):
                pass

        return logs

    def add_log(self, log: CronLog) -> bool:
        """Add a log entry for a job."""
        log_file = self._logs_dir / f'{log.job_id}.json'
        logs = self.get_job_logs(log.job_id)
        logs.append(log)

        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([l.to_dict() for l in logs[-100:]], f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    @property
    def cron_file(self) -> Path:
        return self._cron_file

    @property
    def logs_dir(self) -> Path:
        return self._logs_dir
