#!/usr/bin/env node
// Multi-env CDK app (Pattern A): one Stack instance per deployment stage.
// Each instance carries its own EnvironmentConfig — account, region, and
// monitoring tier — that the framework's PythonLambdaApi uses for tagging,
// log retention, and alarm thresholds.

import 'source-map-support/register'
import * as cdk from 'aws-cdk-lib'
import type { EnvironmentConfig } from '@devex/framework'

import { TransactionifyStack } from '../lib/transactionify-stack'

const ENVIRONMENTS: readonly EnvironmentConfig[] = [
  { stage: 'sandbox', account: '111111111111', region: 'us-east-1', monitoring: 'basic' },
  { stage: 'staging', account: '222222222222', region: 'us-east-1', monitoring: 'enhanced' },
  { stage: 'prod',    account: '333333333333', region: 'us-east-1', monitoring: 'enhanced' },
]

const app = new cdk.App()

for (const environment of ENVIRONMENTS) {
  new TransactionifyStack(app, `transactionify-${environment.stage}`, {
    description: `Transactionify ${environment.stage} — Mocked API stack.`,
    env: { account: environment.account, region: environment.region },
    environment,
  })
}
