import type { PythonLambdaProfile } from '@devex/framework'

export const profile: PythonLambdaProfile = {
  language: 'python',
  serviceName: 'transactionify',
  team: 'transactionify',
  repoUrl: 'https://github.com/JynLeazy1/transactionify',
  workIdPattern: '[A-Z][A-Z0-9]*-\d+',
  awsRegion: 'us-east-1',
  runtime: '3.12',
  packageManager: 'uv',
  sourcePath: 'src/python',
  testCommand: 'pytest --cov=src/python --cov-report=xml --cov-fail-under=80',
  lintCommands: [
    'ruff check src/python',
    'ruff format --check src/python',
  ],
  openApiPath: 'openapi.yaml',
  minCoverage: 80,
}
