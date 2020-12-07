<div align="center" markdown>
<img src="https://i.imgur.com/Ab2GHSQ.png"/>

# Group reference objects into batches

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/group-reference-objects-into-batches)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/group-reference-objects-into-batches)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/group-reference-objects-into-batches&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/group-reference-objects-into-batches&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/group-reference-objects-into-batches&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Labeling for tagging or classification tasks becomes complex when annotation team have to deal with hundreds or thousands of tags or classes. This app groups items from catalog by one or several columns and then splits groups into small batches. 

Let's consider retail case as example:
- We need to label product shelves: draw bounding boxes around every object and assign correct class from catalog
- The size of catalog: 1350 unique items
- The size of annotation team: 150 labelers

<img src="https://thumbs.dreamstime.com/z/pet-products-shelves-supermarket-pet-products-shelves-supermarket-auchan-romania-145486859.jpg" width="400px"/>



# group-reference-objects-into-batches
Reference objects are grouped into batches by columns from CSV catalog.
