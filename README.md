<div align="center" markdown>
<img src="https://i.imgur.com/Ab2GHSQ.png"/>

# Group reference objects into batches

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#Result-JSON-Format">Result JSON format</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/group-reference-objects-into-batches)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/group-reference-objects-into-batches)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/group-reference-objects-into-batches&counter=views&label=views)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/group-reference-objects-into-batches&counter=runs&label=runs&123)](https://supervise.ly)

</div>

# Overview

Labeling for tagging or classification tasks becomes complex when annotation team have to deal with hundreds or thousands of tags or classes. This app groups items from catalog by one or several columns and then splits groups into small batches. This app is a part of complex tagging/classification pipline. For example, you can see all apps from [retail collection](https://ecosystem.supervise.ly/).

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

# How To Run

**Step 1:** Add app to your team from Ecosystem if it is not there.

**Step 2:** Run app 
 
 <img src="https://i.imgur.com/Y5PgfbT.png"/>
 
**Step 3:** What until UI is ready

# How To Use

[![Watch the video](https://i.imgur.com/grDPMed.png)](https://youtu.be/MyrOgn4RpyA)

**Step 1:** Define the path to `CSV` product catalog in `Team Files` and press `Preview catalog` button

Before:
 <img src="https://i.imgur.com/6ds1Rnl.png"/>

After:
 <img src="https://i.imgur.com/xTDnKYt.png"/>
 
 **Step 2:** Define the path to directory with `JSON` reference files that created with the app ["Create JSON with reference items"](https://ecosystem.supervise.ly/apps/create-json-with-reference-items), press `Preview files` button, select files that should be used and then press `Validate` button.
 
Before:
 <img src="https://i.imgur.com/28A6AUg.png"/>

After:
 <img src="https://i.imgur.com/OUM7FBM.png"/>


**Step 3:** Match reference item with column from CSV catalog, choose `groupBy` columns from catalog (order matters), define batch size and press `Create groups` button. Then preview groups. You can change some grouping parameters and press `Create groups` button again. If you satisfied with results, setup save path and press `Save` button. Resulting groups will be saved to `Team Files` in `JSON` format.


Before:
 <img src="https://i.imgur.com/EU4cS1g.png"/>

After:
 <img src="https://i.imgur.com/tWB1Q5G.png"/>
 
**Step 4:** Stop app manually

<img src="https://i.imgur.com/flXfONq.png"/>


# Result JSON format

```json
[
  {
    "batch_index": 0,
    "items_count": 3,
    "group_columns": {
      "category": "Accessories",
      "sub-category": "Portable Power Banks",
      "brand": "Samsung"
    },
    "key_col_name": "upc",
    "references": {
      "6750711": ["..."],
      "7930356": ["..."],
      "9994737": ["..."]
    },
    "references_catalog_info": {
      "6750711": {
        "brand": "Samsung",
        "name": "Samsung Universal 3100mAh Portable External Battery Charger - White",
        "upc": 6750711,
        "weight": "5.6 ounces",
        "category": "Accessories",
        "sub-category": "Portable Power Banks",
        "price": 17.99,
        "merchant": "Bestbuy.com"
      },
      "7930356": {
        "brand": "Samsung",
        "name": "Samsung Universal 3100mAh Portable External Battery Charger - White",
        "upc": 7930356,
        "weight": "5.6 ounces",
        "category": "Accessories",
        "sub-category": "Portable Power Banks",
        "price": 14.84,
        "merchant": "accessorynet"
      },
      "9994737": {
        "brand": "Samsung",
        "name": "Samsung Universal 3100mAh Portable External Battery Charger - White",
        "upc": 9994737,
        "weight": "5.6 ounces",
        "category": "Accessories",
        "sub-category": "Portable Power Banks",
        "price": 22.99,
        "merchant": "Bestbuy.com"
      }
    },
    "catalog_path": "/reference_items/1120-water-catalog.csv"
  },
  {
    "batch_index": 1,
    "...": "..."
  }
]
```

Result JSON - list of objects, that describe every batch of reference objects:
- `batch_index` - index of the batch
- `items_count` - number of items in batch   
- `group_columns` - the names of columns and corresponding values used to group items (`groupBy` operation)
- `key_col_name` - name of the column in CSV catalog that is used to match reference item with correct row from product catalog
- `references` - dictionary with reference examples for every item (format is the same as in [reference items format](https://github.com/supervisely-ecosystem/create-json-with-reference-items#json-format))
- `references_catalog_info` - information from catalog for every reference item
- `catalog_path` - path to the catalog in Team Files