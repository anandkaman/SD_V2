module.exports = {
  apps: [
    {
      name: 'salesdeed-backend',
      script: 'venv/Scripts/python.exe',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      cwd: './sale-deed-processor/backend',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'salesdeed-frontend',
      script: 'npm',
      args: 'start',
      cwd: './sale-deed-processor/fronted',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
