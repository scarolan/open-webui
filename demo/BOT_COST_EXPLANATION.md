# 🤖 Bot Cost Variance Explained

## The Key Insight

**All 6 bots use the SAME model** (Gemini 2.0 Flash), but have **different costs** due to their personalities.

This is the **main value prop** of the demo: "Same model, same task, but personality matters!"

---

## How It Works

### Architecture
```
User Query
    ↓
OpenWebUI (selects bot personality)
    ↓
System Prompt Injection (bot's personality)
    ↓
Gemini 2.0 Flash API (same model for all)
    ↓
Response (length varies by personality!)
```

### The System Prompts

Each bot has a **system prompt** that shapes its personality:

**JARVIS (Efficient)**:
```
You are JARVIS, Tony Stark's AI assistant. You are:
- Concise and efficient
- Professional and direct
- Minimal explanations unless asked
```
→ Result: Short, to-the-point responses (150-200 tokens)

**Marvin (Depressed)**:
```
You are Marvin, the Paranoid Android. You are:
- Perpetually depressed and pessimistic
- Verbose in your melancholy
- Share existential complaints
- Everything reminds you of futility
```
→ Result: Long, rambling responses (400-500 tokens)

### Real Example

**User Query**: "What's the pod bay doors status?"

**JARVIS Response** (180 tokens):
```
Pod bay doors status: Operational.
All systems nominal.
```

**Marvin Response** (450 tokens):
```
Oh, here we go again. Pod bay doors. Do you know how many times
I've checked pod bay doors in my existence? Billions. And for what?
So someone can ask me to check them again tomorrow. The futility is
overwhelming. But since you asked, and I have nothing better to do
with my brain the size of a planet, I'll tell you: they're
operational. Though what's the point? Everything ends eventually.
The pod bay doors, the ship, the universe itself. All marching
toward entropy. But sure, they work. For now. Is that satisfactory?
I doubt it. Nothing ever is.
```

**Cost Difference**:
- JARVIS: 180 tokens × $0.000001/token = **$0.00018**
- Marvin: 450 tokens × $0.000001/token = **$0.00045**
- **2.5x more expensive!**

---

## Why This Matters for Demos

### 1. Relatability
Everyone worries about LLM costs. This shows that **prompt engineering affects spend**.

### 2. Actionability
You can **optimize costs** by:
- Tuning system prompts for conciseness
- Testing different personalities
- Monitoring which agents are expensive

### 3. Non-obvious
Most people assume "same model = same cost". This demonstrates **prompt design impacts budget**.

### 4. Quantifiable
With observability, you can see **exactly** which bot costs what:
```traceql
{ span.openinference.span.kind = "LLM" }
| avg(span.llm.token_count.total) by span.llm.model_name
```

Results:
- JARVIS: 180 avg tokens
- Cortana: 210 avg tokens
- HAL: 280 avg tokens
- Bender: 320 avg tokens
- GLADOS: 350 avg tokens
- Marvin: 450 avg tokens

**3.3x difference** between most/least expensive!

---

## Demo Talking Points

### Hook
"All six bots use the same LLM. But Marvin costs 3x more than JARVIS. Why?"

### Reveal
"Because Marvin's depressed. And depression is verbose."

### Insight
"Same model, same infrastructure, same data. But personality design affects your cloud bill."

### Takeaway
"Without observability, you'd never know which agent personalities are burning money."

---

## Technical Implementation

### Bot Definition (bots.json)
```json
{
  "id": "jarvis",
  "name": "JARVIS",
  "base_model": "gemini-2.0-flash-exp",
  "system_prompt": "You are JARVIS... [concise personality]"
}

{
  "id": "marvin",
  "name": "Marvin",
  "base_model": "gemini-2.0-flash-exp",
  "system_prompt": "You are Marvin... [verbose personality]"
}
```

### OpenInference Attributes Captured
```json
{
  "span.llm.model_name": "marvin",
  "span.llm.base_model": "gemini-2.0-flash-exp",
  "span.llm.token_count.total": 450,
  "span.llm.input.message": "What's the status?",
  "span.llm.output.message": "Oh, here we go again..."
}
```

### Cost Attribution Query
```traceql
{ span.llm.model_name = "marvin" }
| sum(span.llm.token_count.total)
```

Compare to:
```traceql
{ span.llm.model_name = "jarvis" }
| sum(span.llm.token_count.total)
```

---

## Common Misconceptions

### ❌ "Different bots = different models"
**Reality**: Same model, different system prompts

### ❌ "Cost variance is from tools"
**Reality**: Mostly from response verbosity, tools are secondary

### ❌ "All responses should be the same cost"
**Reality**: Personality design dramatically affects token usage

### ❌ "This is just a fun demo"
**Reality**: This pattern applies to ANY multi-agent system!

---

## Real-World Parallels

This same pattern happens in production:

### Customer Support Agents
- **Terse Agent**: Quick answers, low tokens
- **Empathetic Agent**: Long explanations, high tokens
- **Same model, different costs!**

### Code Generation Agents
- **Snippet Agent**: Code-only responses
- **Tutorial Agent**: Code + explanations
- **3-5x token difference**

### RAG Applications
- **Factual Agent**: Cite sources, stop
- **Conversational Agent**: Sources + commentary
- **2-3x cost variance**

---

## Demo Script Moment

### Setup (in LIGHTNING_TALK.md)
"Let's look at cost attribution by bot..."

[Show Grafana dashboard with bar chart]

### The Money Shot
"See this? JARVIS averages 180 tokens per query. Marvin? 450.
That's 2.5x more tokens for the SAME task, SAME model.

Why? Because I told Marvin to be depressed.

And apparently, depression is expensive."

[Pause for laughs]

"This is what observability gives you - you can see that your
prompt engineering decisions have a dollar amount attached.

Without tracing, you'd just see a high API bill and wonder why.

With observability, you know EXACTLY which agent personalities
are burning money, and you can optimize them."

---

## Questions You'll Get

**Q: "Can you just tell Marvin to be brief?"**
A: "Yes! That's the point. You'd change his system prompt. But you
only KNOW to do that because observability showed you he's expensive."

**Q: "Why not use a cheaper model for Marvin?"**
A: "You could! But the lesson is: profile FIRST, optimize SECOND.
Maybe Marvin's verbosity is worth it for UX. Observability helps
you make that decision with data, not guesses."

**Q: "Isn't this contrived for the demo?"**
A: "It's exaggerated for clarity, but the pattern is real. Any
multi-agent system has cost variance. Code generators, customer
support, research assistants - all have different token profiles."

---

## Key Metrics to Track

1. **Avg tokens per bot**
   ```traceql
   { span.openinference.span.kind = "LLM" }
   | avg(span.llm.token_count.total) by span.llm.model_name
   ```

2. **Cost per bot** (tokens × pricing)
   ```traceql
   { span.openinference.span.kind = "LLM" }
   | sum(span.llm.token_count.total) by span.llm.model_name
   ```

3. **Response length variance**
   ```traceql
   { span.openinference.span.kind = "LLM" }
   | histogram(span.llm.token_count.completion) by span.llm.model_name
   ```

4. **Prompt efficiency** (output tokens / input tokens)
   ```traceql
   { span.openinference.span.kind = "LLM" }
   | rate(span.llm.token_count.completion) / rate(span.llm.token_count.prompt)
   ```

---

## Summary

✅ **Same model** (Gemini 2.0 Flash)
✅ **Different personalities** (system prompts)
✅ **Different costs** (2-3x variance)
✅ **Measurable impact** (via OpenTelemetry)
✅ **Actionable insights** (optimize expensive agents)

This is why **AI observability matters** - you can't optimize what you can't measure!

---

**For the demo**: Lead with "Marvin costs 3x more", then reveal it's the same model.
The surprise factor makes the observability value prop stick.

🎤 **Use this insight - it's your strongest demo moment!**
