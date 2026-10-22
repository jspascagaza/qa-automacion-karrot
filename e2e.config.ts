import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';
import { google } from '@ai-sdk/google';
import 'dotenv/config';

export default {
  timeout: 180000,
  targets: [
    {
      engine: web(),
      app: {
        url: process.env.URL_BASE || 'https://devtwo.do5o1l1ov8f4a.amplifyapp.com',
      },
    },
  ],
  agents: {
    default: {
      model: google('gemini-3.8-flash'),
      system: 'Eres un QA tester experto navegando una plataforma web.',
    },
  },
} satisfies E2EConfig;
