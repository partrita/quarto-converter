# Quarto Book Template

This repository is a template for creating a Quarto book hosted on GitHub Pages, with dependencies managed by [Pixi](https://prefix.dev/).

## Project Structure

- `mybook/`: Contains the Quarto book source files (`.qmd`).
- `pixi.toml`: Manages dependencies (Quarto, Python/R libraries).
- `.github/workflows/publish.yml`: GitHub Action to automatically build and publish the book.

## Usage

### Prerequisites

- [Pixi](https://prefix.dev/) installed on your machine.

### Local Development

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/quarto-book-template.git
    cd quarto-book-template
    ```

2.  **Preview the book:**

    Run the following command to install Quarto (if not already cached) and start a live preview server:

    ```bash
    pixi run quarto preview mybook
    ```

    Or if you just want to run the quarto command directly:

    ```bash
    pixi run quarto render mybook
    ```

### Dependencies

This project uses `pixi` to manage dependencies. The default `pixi.toml` includes `quarto`.

To add Python or R dependencies:

```bash
pixi add python pandas  # Example for Python
# or
pixi add r-base r-tidyverse  # Example for R
```

## Deployment

This repository is configured to automatically publish the book to GitHub Pages using GitHub Actions.

1.  **GitHub Settings:**
    *   Go to your repository **Settings** > **Pages**.
    *   Under **Build and deployment**, usually you can leave it as "Deploy from a branch".
    *   After the first successful run of the action, a `gh-pages` branch will be created.
    *   Ensure the **Branch** is set to `gh-pages` and folder to `/(root)`.

2.  **Triggering the Build:**
    *   Pushing to the `main` branch will trigger the workflow.
    *   You can also manually trigger it from the **Actions** tab.

The workflow is defined in `.github/workflows/publish.yml`. It uses the `quarto-dev/quarto-actions/publish` action to build the project in the `mybook` directory and push the result to the `gh-pages` branch.