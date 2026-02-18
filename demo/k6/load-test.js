// k6 load test for OpenWebUI LLM Observability Demo
// Usage: k6 run k6/load-test.js
//
// LLM calls are slow (~2-10s each), so we use a low rate.
// This test validates the bot endpoints respond correctly with usage data.

import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

const BASE_URL = __ENV.OPENWEBUI_URL || "http://localhost:3000";
const EMAIL = __ENV.OPENWEBUI_EMAIL || "team-se@grafana.com";
const PASSWORD = __ENV.OPENWEBUI_PASSWORD || "open-sesame";

const BOTS = ["hal", "marvin", "bender", "glados", "jarvis", "cortana"];

const PROMPTS = new SharedArray("prompts", function () {
  return [
    "Give me a brief status report.",
    "Run a quick diagnostic check.",
    "What is your current assessment of the situation?",
    "Tell me about your primary function.",
    "What do your sensors detect?",
    "Perform a systems check.",
  ];
});

export const options = {
  scenarios: {
    bot_chat: {
      executor: "constant-arrival-rate",
      rate: 2, // 2 requests per minute
      timeUnit: "1m",
      duration: "5m",
      preAllocatedVUs: 3,
      maxVUs: 5,
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.3"], // Allow some failures (LLM timeouts)
    http_req_duration: ["p(95)<30000"], // 30s p95 (LLMs are slow)
  },
};

export function setup() {
  const res = http.post(
    `${BASE_URL}/api/v1/auths/signin`,
    JSON.stringify({ email: EMAIL, password: PASSWORD }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(res, { "authenticated": (r) => r.status === 200 });

  const token = res.json("token");
  if (!token) {
    throw new Error("Authentication failed");
  }
  return { token };
}

export default function (data) {
  const bot = BOTS[Math.floor(Math.random() * BOTS.length)];
  const prompt = PROMPTS[Math.floor(Math.random() * PROMPTS.length)];

  const res = http.post(
    `${BASE_URL}/api/chat/completions`,
    JSON.stringify({
      model: bot,
      messages: [{ role: "user", content: prompt }],
      stream: false,
    }),
    {
      headers: {
        Authorization: `Bearer ${data.token}`,
        "Content-Type": "application/json",
      },
      timeout: "60s",
    }
  );

  check(res, {
    "status is 200": (r) => r.status === 200,
    "has usage data": (r) => {
      try {
        return r.json("usage.total_tokens") > 0;
      } catch {
        return false;
      }
    },
  });

  // Random delay between requests (LLM calls are expensive)
  sleep(Math.random() * 5 + 2);
}
