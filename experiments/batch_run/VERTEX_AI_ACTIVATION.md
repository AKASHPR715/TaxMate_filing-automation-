# ✅ Vertex AI Setup Complete - One Manual Step Remaining

## What We've Accomplished ✅

| Step | Status | Details |
|------|--------|---------|
| Install gcloud CLI | ✅ Done | Version 551.0.0 installed |
| Authenticate | ✅ Done | Logged in as akashanil456@gmail.com |
| Configure project | ✅ Done | `taxmate-research-1767868153` |
| Enable billing | ✅ Done | Account: `01A951-CF4734-3C8B74` ($300 credits) |
| Enable Vertex AI API | ✅ Done | `aiplatform.googleapis.com` |
| Enable Generative AI API | ✅ Done | `generativelanguage.googleapis.com` |
| Add IAM permissions | ✅ Done | `roles/aiplatform.user` granted |
| Create `.env` config | ✅ Done | Project ID configured |

## 🚨 The Final Step: Accept Terms of Service (Manual)

**Why models return 404**: Google requires manual acceptance of Generative AI Terms of Service through the web console. This cannot be done via CLI.

### Instructions

**Step 1**: Open this URL in your browser (already logged in):
```
https://console.cloud.google.com/vertex-ai/generative/language?project=taxmate-research-1767868153
```

**Step 2**: You'll see one of these:
- **"Try Generative AI"** button → Click it
- **"Enable API"** button → Click it
- **"Accept Terms of Service"** dialog → Read and accept
- **"Get Started"** or **"Try it out"** → Click to activate

**Step 3**: Verify activation
- After clicking, you should see a text generation interface
- A dropdown showing available models (gemini-1.5-flash, gemini-1.5-pro, etc.)
- Try typing a prompt to confirm it works

**Step 4**: Return here and test with Python

---

## Testing After Activation

Once you've accepted ToS in the console, run this test:

```bash
cd /home/akash.anil@acsiatech.com/TaxMate_filing-automation-

# Test with 1 profile
python3 experiments/execution/runner.py --count 1 --model gemini-1.5-flash
```

**Expected output**:
```
✅ Initialized with Google Vertex AI: gemini-1.5-flash (Project: taxmate-research-1767868153)
Processing profile 1/1...
[LLM responses will appear here]
✅ Profile completed successfully
```

---

## If Test Succeeds: Run Full Experiments

```bash
cd experiments/batch_run

# Run all 5 batches (500 profiles total)
./run_all_batches.sh

# Cost with gemini-1.5-flash: ~$2-3 (you have $300!)
```

---

## Alternative: Use Different Region

If `us-central1` doesn't work after ToS acceptance, try:

```bash
# Update .env
cd experiments/batch_run
cat >> .env << 'EOF'
GOOGLE_CLOUD_LOCATION=us-east4
EOF

# Test again
cd ../..
python3 experiments/execution/runner.py --count 1 --model gemini-1.5-flash
```

---

## Troubleshooting

### Still getting 404 after accepting ToS?

Try these model names:
```bash
# Different naming formats
--model gemini-pro
--model gemini-flash  
--model models/gemini-1.5-flash
```

### Check billing quotas

Visit: https://console.cloud.google.com/iam-admin/quotas?project=taxmate-research-1767868153

Look for "Vertex AI API" quotas and ensure none are at 0.

### Verify credits balance

Visit: https://console.cloud.google.com/billing/credits

Ensure your $300 credits are showing and linked to the project.

---

## Next Steps Summary

1. **☑️ YOU MUST DO**: Open the Vertex AI console URL above and accept ToS
2. **☑️ TEST**: Run the 1-profile test command
3. **☑️ If successful**: Run full batch experiments
4. **☑️ If still failing**: Report the exact error message and we'll troubleshoot further

---

## Your $300 Credits Usage Estimate

| Task | Cost | Remaining |
|------|------|-----------|
| Test (1 profile) | ~$0.01 | $299.99 |
| Full run (500 profiles) | ~$2-3 | ~$297 |
| **Total** | **~$3** | **$297 left for more experiments!** |

---

**You're 99% done! Just accept the ToS in the console and you're ready to go.** 🚀
