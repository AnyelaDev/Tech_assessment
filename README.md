# Technical Assessment

## Task: 
The task is to use **Claude Code** to reimagine a project you previously worked on. You are free to use whatever language, frameworks, and tools you wish. You do not need to finish the entire project or even have anything working -- the only constraint is to spend **no more than 6 hours on this. The deliverable is a GitHub repo with the project code and a README.md file containing a reflection on your experiences using the tool. In particular, discuss how far you got, what challenges you ran into, and how the architecture or approach taken compared to the previous version you worked on.

## Log
- **17:13** I started with reimagining how to merge two of my projects into one, and using a different stack of tech. I am also hoping to add AI into it, because, why not?
- **17:23** I will start with a readme.md as a map of the current status of development "user facing" style. I will also keep a folder for planning markdown files. I think it helps me keep it all tidy when working with Claude. 
- **18:45** AI integration implementation in the backend done. I tried this time to go backend first, front end second, but It is making my life harder than necessary. Time to add ui and make some progress.
- **21:20** UI is working. I had a bunch of problems because I accidentally added a space ad the end of a folder name. It took a while for claude and me to figure it out. 
- **01:06** I am over the 6 hour mark. I am not very happy because I spent about 90 minutes total wresling with the space in the name mistake, which affected tests and was hard to spot. Probably around 4,5 hours of effective work. I also tried to use hugging face API to run inferences remotely. I though it was going to be much easier, I ended up just using claude for it. 
- **01:49** AI integration is working, promts are working well, I could try to make them better but polishing will be left for another time. 
- **03:22** I am having too much fun working. I missed this! however, I am very tired. It's pretty late!

---

## Work Timeline and Progress

| Event | Time | Commit Link | Major Progress and Challenges |
|-------|------|-------------|------------------------------|
| **Time I started** | 17:13 | *Project initialization* | Started reimagining project merge with new tech stack + AI integration |
| **6 hours of work mark** | 01:06 | [`ce16694`](../../commit/ce16694) - UI fixes (01:04)<br>[`b8cb2ce`](../../commit/b8cb2ce) - backend fixes (01:02) | UI working, but lost ~90 min to space-in-folder-name bug. HuggingFace API pivot to Claude |
| **6 hours effective work** | ~02:30 | [`a2c01c4`](../../commit/a2c01c4) - Plan refining (02:23) | AI integration working, prompts functional, plan refinement phase |
| **Too tired to continue (8.5 hours)** | 03:30 | [`ed2c743`](../../commit/ed2c743) - Issues 6 & 7 completed (03:25)<br>[`ce5c14e`](../../commit/ce5c14e) - Enhanced models with validation (03:20) | **Final push:** Successfully completed major feature work - enhanced models, task_id, priority fields, validation |

**Key Technical Pivots:**
- 🔄 **Backend-first approach** proved more challenging than expected
- 🚫 **HuggingFace API integration failed** → switched to Claude Sonnet
- 🐛 **Space-in-folder-name bug** cost 90 minutes of debugging time
- ✅ **AI integration successful** with working prompts and inference

