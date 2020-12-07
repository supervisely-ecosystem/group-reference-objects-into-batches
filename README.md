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

Labeling for tagging or classification tasks becomes complex when annotation team have to deal with hundreds or thousands of tags or classes. This app groups items from catalog by one or several columns and then splits groups into small batches. This app is a part of complex tagging/classification pipline. For example, you can see all apps from retail collection [TODO: add link]().

Let's consider retail case as example:
- We need to label product shelves: draw bounding boxes around every object and assign correct class from catalog
- The size of catalog: 1350 unique items
- The size of annotation team: 150 labelers
- Images look like this:
<img src="https://thumbs.dreamstime.com/z/pet-products-shelves-supermarket-pet-products-shelves-supermarket-auchan-romania-145486859.jpg" width="400px"/>

Put bounding box around every object - it's a feasible task. But it is hard and time consuming to assign correct product identifier from huge catalog to every bbox. One of the approaches is to split catalog across all labelers: in our case `1350 unique items` / `150 labelers` = `9 items in a batch`. Labeler will work with his batch the following way: go through all bboxes and match them with only 9 items. 

Key **advantages** of this approach: 
- labeler knows his batch very well: it's easy to keep in mind 9 items
- the chance of error is reduced significantly
- if bbox is matched with one of 9 items from batch it takes just few clicks from labeler to assign correct tag

# group-reference-objects-into-batches
Reference objects are grouped into batches by columns from CSV catalog.
