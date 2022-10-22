# DupCatch: The Anki Duplicates Finder
<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO
<br />
<div align="center">
  <a href="https://github.com/Mike7154/DupCatch">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->
<h3 align="center">DupCatch V2.0.1.beta</h3>

  <p align="center">
    The Anki Duplicates Finder
    <br />
    <!--
    <a href="https://github.com/Mike7154/DupCatch"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Mike7154/DupCatch">View Demo</a>
    ·
    -->
    <a href="https://github.com/Mike7154/DupCatch/issues">Report Bug</a>
    ·
    <a href="https://github.com/Mike7154/DupCatch/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
<!--
[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->
### Description
  I built to identify duplicate notes in Anki. The built in Anki tool only works if the field is identical. This tool will calculate a similarity score between each note-note pair and rank the most similar notes to identify the non-identical duplicates

  There are two functions.
  1. Find Duplicates
   * This will tag all of the likely duplicate pairs (for review) sorted by most similar based on the algorithm
  2. Merge
   * You can use this tool to merge duplicate fields or tags.
### Built With

* [![Python][Python]][Python-url]
<!--
<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->
<!-- GETTING STARTED -->
## Getting Started
  I have only tested this on Windows running python 3.9, but it should work on other operating systems as well
### Prerequisites
* Python 3.9 +
* Python libraries from requirements.txt

### Installation

1. Clone or download and unzip the repo
  ```sh
  git clone https://github.com/Mike7154/DupCatch.git
  ```
2. Install dependencies (must have python installed and mapped)
  ```sh
  pip install -r requirements.txt
  ```
  or
  ```sh
  py -m pip install -r requirements.txt
  ```
3. You can verify the installation by running:
```sh
cd path/to/DupCatch
py dupcatch.py
```
or
```sh
cd path/to/DupCatch
python dupatch.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

1. Copy the desired Anki package file (*.apkg, *.colpkg) to 'Dupcatch/anki_collection'

2. Modify the settings.yml (or settings_template.yml file if settings.yml doesn't yet exist)
 * If you are doing a 'Duplicates' run, at least modify the 'Duplicates' section in settings.yml
 * If you are doing a 'Merge' run, at least modify the 'Merge' section in settings.yml
3. Run the Script
  ```sh
  cd path/to/DupCatch
  python -m pip install -r requirements.txt
  python dupcatch.py -r
  ```
  * For a Merge run use ```python dupcatch.py -m ```

3. The tool will output a new *.apkg file into DupCatch/anki_collection which will include only notes that were modified
4. Review the results in Anki (I recommend using the Special Fields Addon to choose whether you want tags or a full import)
5. Tag the notes to merge fields, tags, or mark as 'not duplicate' or 'covered_by'
 * only the merge tags are directional, and you only tag the receiving note.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/Mike7154/DupCatch/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

GNU General Public License. See `LICENSE.txt` for more information.
You can copy, modify, and distribute this software as you please.
If you want to use this tool in proprietary software, contact me and I will send a private license agreement.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - m6611022@gmail.com

Project Link: [https://github.com/Mike7154/DupCatch](https://github.com/Mike7154/DupCatch)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Mike7154/DupCatch.svg?style=for-the-badge
[contributors-url]: https://github.com/Mike7154/DupCatch/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Mike7154/DupCatch.svg?style=for-the-badge
[forks-url]: https://github.com/Mike7154/DupCatch/network/members
[stars-shield]: https://img.shields.io/github/stars/Mike7154/DupCatch.svg?style=for-the-badge
[stars-url]: https://github.com/Mike7154/DupCatch/stargazers
[issues-shield]: https://img.shields.io/github/issues/Mike7154/DupCatch.svg?style=for-the-badge
[issues-url]: https://github.com/Mike7154/DupCatch/issues
[license-shield]: https://img.shields.io/github/license/Mike7154/DupCatch.svg?style=for-the-badge
[license-url]: https://github.com/Mike7154/DupCatch/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/https://www.linkedin.com/in/michaelelarsen15/
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/Python-000000?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com
