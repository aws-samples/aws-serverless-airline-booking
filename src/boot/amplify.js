import Amplify from 'aws-amplify'
import { Auth } from '@aws-amplify/auth'
import awsconfig from '../aws-exports'
import '@aws-amplify/ui-vue'

const logLevel = process.env.LOG_LEVEL || 'INFO'
Amplify.configure(awsconfig)
Auth.configure(awsconfig)
Amplify.Logger.LOG_LEVEL = logLevel
