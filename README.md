# PlanExe-web on GitHub Pages

Github pages is used for the [planexe.org](https://planexe.org/) static website. This [github repo](https://github.com/PlanExeOrg/PlanExe-web) contains the website content.

Links:

- [https://planexe.org/](https://planexe.org/)
- [https://github.com/PlanExeOrg/PlanExe](https://github.com/PlanExeOrg/PlanExe)
- [PlanExe Discord](https://planexe.org/discord)


## Install the dependencies

**Ruby 3.3 required.** GitHub Pages uses Ruby 3.3.4; Ruby 4.x is not yet supported by the Jekyll/github-pages ecosystem.

If Homebrew updated you to Ruby 4.x, use Ruby 3.3:

```bash
brew install ruby@3.3
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
```

Then:

```bash
PROMPT> bundle install
```

## Run the server on localhost

```bash
PROMPT> bundle exec jekyll serve
http://127.0.0.1:4000
```

or, if the port is occupied.

```bash
PROMPT> bundle exec jekyll serve --port 4001
http://127.0.0.1:4001
```

## Run the server on all network interfaces (for mobile testing)

```bash
PROMPT> bundle exec jekyll serve --host 0.0.0.0
http://0.0.0.0:4000
```

Access from your phone using your computer's local IP address (e.g., `http://192.168.1.100:4000`)
