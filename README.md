# Senior AWS DevOps interview prep

This is a 60-day study guide for senior DevOps, cloud infrastructure, and SRE interviews. The lessons start with what happens in a real system. Then we work through failures, look at the evidence, and practice explaining what to do next in our own words.

> **[Open the GitHub Pages study guide →](https://tech-sayantan.github.io/senior-devops-interview-prep/)**
>
> [Curriculum](https://tech-sayantan.github.io/senior-devops-interview-prep/curriculum/) · [Day 1 lesson](https://tech-sayantan.github.io/senior-devops-interview-prep/days/day-01-request-path/)

## Start here

- [The 60-day study plan](60-day-study-plan.md) covers the full syllabus and interview practice schedule.
- [Day 1 · DNS, TCP, TLS, and HTTP](days/day-01-request-path.md) walks through a request, explains common interview questions, and includes two production scenarios and a Mac lab.

## CI/CD and release management

Follow a change through the pipeline, then use production evidence to decide whether to keep releasing or stop.

1. [Day 29 · CI/CD and Docker artifacts](days/day-29-cicd-and-artifacts.md)
2. [Day 30 · Jenkins and Groovy pipelines](days/day-30-jenkins-pipelines.md)
3. [Day 31 · GitHub Actions](days/day-31-github-actions.md)
4. [Day 33 · Release management](days/day-33-release-management.md)

## Updating the site

For each day, begin with the agreed lesson in a `day-*.md` file under `days/`. Put diagrams and other study aids alongside the explanations they support. Keep the conversational reasoning, worked scenarios, and small lab when there is one. GitHub Actions builds the site from those same files when updates reach `main`.
