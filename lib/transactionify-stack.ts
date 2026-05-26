// Transactionify Stack — refactored to consume `@devex/framework`.
//
// Before: 187 lines of repeated CDK boilerplate (5 Lambdas × function + grant
// + integration + route + 6 hardcoded tags). After: declarative route list +
// one `PythonLambdaApi` instantiation; the framework provisions the table,
// HTTP API, authorizer, per-route Lambdas, and FinOps tag enforcement.

import * as cdk from 'aws-cdk-lib'
import { PythonLambdaApi, type RouteDefinition } from '@devex/framework'
import { Construct } from 'constructs'

import { profile } from '../devex.profile'

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
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    // NOTE (PoC scope): the upstream baseline included a `provisioningLambda`
    // that received `table.grantWriteData(...)` but was NOT exposed as an API
    // route. It's intentionally dropped here while we evaluate adding an
    // `extraGrants?: ExtraGrant[]` prop to `PythonLambdaApiProps` for
    // non-route Lambdas — additive, non-breaking. Tracked as an inner-source
    // contribution opportunity.
    new PythonLambdaApi(this, 'Api', {
      serviceName: profile.serviceName,
      runtime: profile.runtime,
      sourcePath: profile.sourcePath,
      authorizerHandler: 'transactionify.handlers.authorizer.main.handler',
      routes: ROUTES,
      environment: {
        stage: 'sandbox',
        account: props?.env?.account ?? process.env.CDK_DEFAULT_ACCOUNT ?? '',
        region: props?.env?.region ?? process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
        monitoring: 'basic',
      },
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
