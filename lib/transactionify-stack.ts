// Transactionify Stack — refactored to consume `@devex/framework`.
//
// Before: 187 lines of repeated CDK boilerplate (5 Lambdas × function + grant
// + integration + route + 6 hardcoded tags). After: declarative route list +
// one `PythonLambdaApi` instantiation; the framework provisions the table,
// HTTP API, authorizer, per-route Lambdas, and FinOps tag enforcement.

import * as cdk from 'aws-cdk-lib'
import {
  PythonLambdaApi,
  type EnvironmentConfig,
  type RouteDefinition,
} from '@devex/framework'
import { Construct } from 'constructs'

import { profile } from '../devex.profile'

export interface TransactionifyStackProps extends cdk.StackProps {
  readonly environment: EnvironmentConfig
}

const ROUTES: readonly RouteDefinition[] = [
  {
    path: '/api/v1/accounts',
    method: 'POST',
    handler: 'transactionify.handlers.api.rest.account.create.main.handler',
    permission: 'readwrite',
  },
  {
    path: '/api/v1/accounts/{account_id}/payments',
    method: 'POST',
    handler: 'transactionify.handlers.api.rest.payment.create.main.handler',
    permission: 'readwrite',
  },
  {
    path: '/api/v1/accounts/{account_id}/balance',
    method: 'GET',
    handler: 'transactionify.handlers.api.rest.balance.get.main.handler',
    permission: 'read',
  },
  {
    path: '/api/v1/accounts/{account_id}/transactions',
    method: 'GET',
    handler: 'transactionify.handlers.api.rest.transaction.list.main.handler',
    permission: 'read',
  },
]

export class TransactionifyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: TransactionifyStackProps) {
    super(scope, id, props)

    new PythonLambdaApi(this, 'Api', {
      serviceName: profile.serviceName,
      runtime: profile.runtime,
      sourcePath: profile.sourcePath,
      authorizerHandler: 'transactionify.handlers.authorizer.main.handler',
      routes: ROUTES,
      environment: props.environment,
      // The `Provisioning` Lambda is internal — registers a new tenant by
      // creating their initial API key + account records. NOT exposed as an
      // API route (callers reach it via SDK invoke from an off-platform CLI).
      // Restored upstream parity using `extraGrants`, an inner-source PR
      // added to the framework after the first adoption surfaced the gap.
      extraGrants: [
        {
          id: 'Provisioning',
          handler: 'transactionify.handlers.provisioning.main.handler',
          permission: 'write',
          description:
            'Registers a new user by generating an API key. Not exposed as an API endpoint.',
        },
      ],
      tags: {
        'finops:Project': 'Transactionify',
        'finops:Service': 'Transactionify API',
        'finops:Team': profile.team,
        'finops:Owner': 'jorge.flores',
        'project-type': 'api',
      },
      tagSeverity: profile.tagSeverity,
    })
  }
}
