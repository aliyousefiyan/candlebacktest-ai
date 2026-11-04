# Publishing this standalone community repository

Suggested repository name: `candlebacktest-ai` (independent from `candleaudit`).

Create a **new, empty public repository** on GitHub. Do not import this code into `candleaudit` or into any personal strategy repository. Do not include API keys, Binance credentials, commercial market data or proprietary Pine/strategy code.

If using the source ZIP, extract it so the files appear in the repository root, then run:

```bash
git init -b main
git add .
git commit -m "Initial free CandleBacktest AI MVP with external AI prompt"
git remote add origin https://github.com/OWNER/candlebacktest-ai.git
git push -u origin main
```

Alternatively, if you have the `.bundle` archive, you can clone it locally then add the GitHub remote. Confirm `python -m unittest discover -s tests -q` succeeds and GitHub Actions tests pass. This is not a certified ChatGPT/OpenAI app and GitHub publication does not trigger app approval.

After publication, collect feedback on usability and schema gaps before expanding advanced indicators. Avoid claiming financial profitability or TradingView parity without independent evidence.
