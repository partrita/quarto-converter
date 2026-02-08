다음 내용을 `GEMINI.md`에 넣으면 요구하신 워크플로를 꽤 명확하게 설명할 수 있습니다. [quarto](https://quarto.org/docs/publishing/github-pages.html)

***

# Quarto Book + GitHub Pages 배포 가이드 (with Pixi)

이 리포지토리는 **Quarto book**을 GitHub Pages로 배포하기 위한 프로젝트입니다.  
의존성 관리는 **Pixi**로 수행하며, GitHub에 첫 푸시를 하기 전에 반드시 로컬에서 `pixi run quarto publish gh-pages`를 한 번 실행해야 합니다. [mechatronics3d.substack](https://mechatronics3d.substack.com/p/unlocking-the-power-of-pixi-and-quarto)

## 1. 사전 준비

1. Pixi 설치  
   - 아직 Pixi가 설치되지 않았다면, 공식 문서를 참고해 로컬 환경에 Pixi를 설치합니다. [mechatronics3d.substack](https://mechatronics3d.substack.com/p/unlocking-the-power-of-pixi-and-quarto)

2. 이 리포지토리 클론

```bash
git clone <THIS_REPO_URL>
cd <THIS_REPO_DIR>
```

3. Pixi 환경 준비

```bash
# 환경 생성 및 의존성 설치
pixi install

# (선택) 환경 안에서 쉘 실행
pixi shell
```

`pixi.toml`에 정의된 대로 Quarto 및 기타 필요한 도구들이 설치됩니다. [mechatronics3d.substack](https://mechatronics3d.substack.com/p/unlocking-the-power-of-pixi-and-quarto)

## 2. 로컬에서 Quarto Book 검사 및 빌드

항상 **Quarto book 폴더 구조에 문제가 없는지** 확인한 후 빌드/배포를 진행해야 합니다. [github](https://github.com/quarto-dev/quarto-cli/discussions/7776)

대표적인 체크리스트:

- `_quarto.yml` 혹은 `mybook/_quarto.yml`에 정의된 `project` 및 `book` 설정이 올바른지  
- `index.qmd`가 존재하는지  
- `chapters` 또는 `book:` 섹션 아래에 나열된 모든 `.qmd` 파일이 실제로 존재하는지  
- 이미지 경로(`images/...`)가 깨지지 않는지 [quarto](https://quarto.org/docs/publishing/github-pages.html)

로컬에서 book을 렌더링 해보려면:

```bash
# 프로젝트 루트에서
pixi run quarto render

# 특정 book 폴더가 있을 경우 (예: mybook/)
pixi run quarto render mybook
```

빌드가 에러 없이 완료되는지 항상 먼저 확인합니다. [github](https://github.com/quarto-dev/quarto-cli/discussions/7776)

## 3. 첫 배포 전: 로컬에서 `quarto publish gh-pages` 실행

GitHub Actions를 통해 자동 배포를 사용하려면, **반드시 최초 한 번은 로컬에서 publish 명령을 실행해야 합니다.** [github](https://github.com/quarto-dev/quarto-actions/blob/main/examples/example-01-basics.md)

```bash
# 프로젝트 루트에서
pixi run quarto publish gh-pages
```

이 명령은 다음을 수행합니다. [github](https://github.com/quarto-dev/quarto-cli/discussions/3199)

- Quarto book을 렌더링  
- 결과물을 이용해 `gh-pages` 브랜치를 구성  
- GitHub Pages 설정에 사용되는 `_publish.yml` 파일을 생성  

이 과정을 통해 이후 GitHub Actions에서 `quarto publish gh-pages`를 사용할 수 있는 설정이 준비됩니다. [github](https://github.com/quarto-dev/quarto-actions/blob/main/examples/example-01-basics.md)

## 4. GitHub에 푸시하면 자동 배포

최초 로컬 publish 후, 리포지토리를 GitHub에 푸시하면 **GitHub Actions 워크플로가 자동으로 실행되어 GitHub Pages에 배포**되도록 설정합니다. [quarto](https://quarto.org/docs/publishing/github-pages.html)

예시 워크플로(요약):

```yaml
name: Quarto Publish

on:
  push:
    branches: main
  workflow_dispatch:

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Quarto
        uses: quarto-dev/quarto-actions/setup@v2

      - name: Render and Publish
        uses: quarto-dev/quarto-actions/publish@v2
        with:
          target: gh-pages
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

이 설정이 리포지토리의 `.github/workflows/` 아래에 포함되어 있으면, `main` 브랜치로 푸시할 때마다 book이 다시 렌더링되고 `gh-pages` 브랜치로 배포됩니다. [github](https://github.com/quarto-dev/quarto-actions/blob/main/examples/example-01-basics.md)

## 5. 항상 지켜야 할 원칙

- 새로 문서(장)이나 이미지를 추가했을 때는,  
  - Quarto book 설정(`_quarto.yml` 등)에 챕터가 제대로 등록되어 있는지,  
  - 실제 파일 경로와 이미지 경로가 맞는지 **항상 먼저 확인**합니다. [quarto](https://quarto.org/docs/publishing/github-pages.html)
- 로컬에서 `pixi run quarto render`로 빌드가 깨지지 않는지 확인한 뒤 커밋/푸시합니다. [mechatronics3d.substack](https://mechatronics3d.substack.com/p/unlocking-the-power-of-pixi-and-quarto)
- GitHub Pages에 문제가 생기면,  
  - `gh-pages` 브랜치가 정상적으로 갱신되고 있는지,  
  - GitHub Actions 로그에서 `quarto publish gh-pages` 단계에 에러가 없는지 확인합니다. [github](https://github.com/quarto-dev/quarto-cli/discussions/7776)

이 과정을 따르면, Pixi로 의존성을 관리하면서 로컬에서 한 번 `pixi run quarto publish gh-pages`를 실행하고, 이후에는 푸시할 때마다 자동으로 Quarto book이 GitHub Pages에 배포되는 워크플로를 유지할 수 있습니다. [github](https://github.com/quarto-dev/quarto-actions/blob/main/examples/example-01-basics.md)
