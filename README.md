# 🎭 The Imposter Mystery - Statistics Explorer

An interactive web-based learning tool for teaching probability and statistics through the real-world "Jen scenario" - where one player was selected as imposter 2 out of 3 times in a social deduction game.

## 🎯 Educational Goals

This tool teaches high school students:

1. **Probability Fundamentals**
   - Basic probability calculations (fractions like 3/17)
   - Compound probability (multiple events)
   - Independent events and multiplication

2. **Statistical Concepts**
   - Law of Large Numbers (convergence)
   - Expected vs. actual outcomes
   - Distribution patterns
   - Statistical variation

3. **Experimental Design**
   - Why we run multiple trials
   - How simulations validate theory
   - The role of sample size in accuracy

## 🚀 Quick Start

1. **Open the tool**: Simply open `index.html` in any modern web browser
2. **Watch the story**: See what happened to Jen across 3 game rounds
3. **Run simulations**: Try different run counts (10, 100, 1,000, 10,000)
4. **Discover patterns**: Watch how results converge toward theoretical probability

## 📊 The Jen Scenario

**What Happened:**
- Round 1: 3 imposters out of 17 players → Jen was selected ✓
- Round 2: 3 imposters out of 17 players → Jen was NOT selected ○
- Round 3: 2 imposters out of 18 players → Jen was selected ✓

**The Question:** Is getting imposter 2 out of 3 times lucky, unlucky, or just random?

**The Math:**
- Probability: 1.61% (or 1 in 62)
- Formula: (3/17) × (14/17) × (2/18) × 3 = 0.0161

## 🎓 How to Use This Tool

### For Students

**Discovery Learning Path:**

1. **Start Small (10 simulations)**
   - Notice how results vary wildly
   - Might see 0%, 20%, or even 30%
   - This is normal! Small samples are unpredictable

2. **Scale Up (100 simulations)**
   - Results start getting closer to theory
   - Still some variation, but converging
   - Pattern becomes clearer

3. **Go Big (1,000-10,000 simulations)**
   - Results very close to 1.61%
   - Distribution clearly visible
   - Law of Large Numbers in action!

4. **Experiment**
   - Change the game settings
   - Try different player/imposter counts
   - See how probabilities change

### For Educators

**Recommended Lesson Flow:**

1. **Hook (5 minutes)**
   - Show the intro screen
   - Tell the Jen story
   - Ask: "Lucky or unlucky?"

2. **Exploration (15 minutes)**
   - Students run 10 simulations
   - Discuss variable results
   - Run 100, then 1,000
   - Observe convergence

3. **Concepts (10 minutes)**
   - Click "Learn More" buttons
   - Discuss Law of Large Numbers
   - Explain theoretical calculation

4. **Extension (Optional)**
   - Custom scenarios
   - Compare different setups
   - Calculate other probabilities

## 💡 Key Learning Moments

### Moment 1: "Why are my results so different?"

**With 10 simulations:** Results vary dramatically
- **Teaching point:** Small samples don't represent true probability
- **Analogy:** Flipping a coin 10 times might give 7 heads - doesn't mean it's unfair

### Moment 2: "It's getting closer to 1.61%!"

**With 1,000+ simulations:** Results converge
- **Teaching point:** Law of Large Numbers
- **Real-world:** Why polls need large samples, why casinos always win

### Moment 3: "The distribution looks like a curve"

**Histogram pattern:** Most results near middle, fewer at extremes
- **Teaching point:** Normal distribution basics
- **Extension:** Binomial distribution (for advanced students)

## 🔧 Technical Features

### Performance
- Runs 10,000 simulations in < 500ms
- Live progress updates every 1% of completion
- Non-blocking UI (stays responsive)
- Optimized with Fisher-Yates shuffle algorithm

### Visualizations
- **Animated Story**: Watch the 3 rounds play out
- **Progress Bar**: Real-time simulation tracking
- **Distribution Histogram**: See patterns emerge
- **Theory vs Reality Cards**: Compare predictions to results
- **Text Breakdown**: Detailed percentage breakdown

### User Controls
- **Preset Buttons**: Quick access (10, 100, 500, 1K, 10K runs)
- **Custom Input**: Any count from 1 to 100,000
- **Game Settings**: Adjust players and imposters per round
- **Reset Button**: Return to Jen scenario

## 📱 Compatibility

**Browsers:**
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (iOS/Android)

**Requirements:**
- Modern web browser with JavaScript enabled
- Internet connection (for Chart.js CDN on first load)
- No installation or build process needed

## 🎨 Color Coding

- **Teal (#4ECDC4)**: Primary actions and default bars
- **Coral (#FF6B6B)**: Jen's selections and highlights
- **Yellow (#FFE66D)**: Discovery moments and accents

## 📐 The Mathematics

### Theoretical Probability Calculation

For getting selected exactly 2 times out of 3 rounds:

```
P(X=2) = P(selected in rounds 1,2 only) +
         P(selected in rounds 1,3 only) +
         P(selected in rounds 2,3 only)

Round 1: p₁ = 3/17 = 0.176
Round 2: p₂ = 3/17 = 0.176
Round 3: p₃ = 2/18 = 0.111

P(X=2) = [p₁ × p₂ × (1-p₃)] +
         [p₁ × (1-p₂) × p₃] +
         [(1-p₁) × p₂ × p₃]

       = [0.176 × 0.176 × 0.889] +
         [0.176 × 0.824 × 0.111] +
         [0.824 × 0.176 × 0.111]

       = 0.0275 + 0.0161 + 0.0161
       = 0.0161 (1.61%)
```

### Why This Works

- Each round is **independent** (previous rounds don't affect future ones)
- We use **multiplication** for "AND" events (both Round 1 AND Round 2)
- We use **addition** for "OR" events (scenario 1 OR scenario 2 OR scenario 3)
- This is the **binomial distribution** formula for n=3, k=2, with varying p

## 🚀 Next Steps (Phase 2)

After mastering Phase 1 (statistical validation), students can explore:

- **Phase 2: Full Gameplay Simulation**
  - AI agents playing the actual game
  - OpenRouter-powered decision making
  - Realistic imposter detection strategies
  - Natural language clue generation

## 📝 Credits

**Created for:** High school statistics education
**Concepts:** Probability, Law of Large Numbers, Binomial Distribution
**Visualization:** Chart.js v4.4.0
**Inspired by:** Real gaming experience and statistical curiosity

## 🤝 Contributing

This is an educational tool. Improvements welcome:

- Additional "Learn More" content
- More preset scenarios
- Accessibility enhancements
- Mobile UX improvements
- Translation to other languages

## 📄 License

Free for educational use. Share with students, teachers, and learners!

---

**Remember:** The goal isn't just to show *that* simulations work - it's to help students *discover* the Law of Large Numbers through hands-on experimentation. Let them be surprised by the convergence!

🎲 Happy exploring! 🎭
