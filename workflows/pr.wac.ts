import { Workflow } from '@github-actions-workflow-ts/lib'

import {
  cdkSynthJob,
  contractValidationJob,
  doraSummaryJob,
  smallTestsJob,
  workIdValidationJob,
} from '@devex/framework'

import { profile } from '../devex.profile'

const workId = workIdValidationJob(profile)
const smallTests = smallTestsJob(profile).needs([workId])
const contracts = contractValidationJob(profile).needs([workId])
const synth = cdkSynthJob(profile).needs([smallTests, contracts])
const dora = doraSummaryJob(profile).needs([workId, smallTests, contracts, synth])

export const prPipeline = new Workflow('pr', {
  name: 'PR Pipeline (Golden Path)',
  on: { pull_request: { branches: ['main'] } },
})
  .addJob(workId)
  .addJob(smallTests)
  .addJob(contracts)
  .addJob(synth)
  .addJob(dora)
