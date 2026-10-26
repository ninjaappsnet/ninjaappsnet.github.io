---
title: Maps
description: Draw filled and bubble maps from countries, states, cities or coordinates, offline. Learn how places match and how to fix the ones that do not.
slug: maps
date: 2026-10-26
order: 13
---
If your data has places in it, a map is often the quickest way to see where the numbers are. FlectoBI draws two kinds of map, and it does so without sending anything over the network. The shapes and the place names ship inside the app.

## Two kinds of map

- A **Filled Map** colours countries, states or regions by a Value. Use it for totals per place, such as revenue by country.
- A **Bubble Map** puts a bubble on each place, sized by a Value. Use it for cities, stores or any point with coordinates.

Add either one with **Add Visual**. Bubbles are sized by area, so a place with twice the value has twice the area. A size legend shows three circles at round values.

![The Map Page of the Sales Sample: a bubble map of revenue by store, and a filled map of revenue by state or region with a note that Madrid is outside this view.](report-map.webp "The Map Page has both kinds of map.")

## Fill the Field Wells

### A Filled Map

1. Choose a **Location** Column, such as a country or a state.
2. Choose a **Colour** Value and its Aggregation, such as **Sum** of Revenue.
3. Optionally fill **Country** and **Region** to help FlectoBI match places.

### A Bubble Map

1. Choose a **Location** Column, or choose **Latitude** and **Longitude** Columns instead.
2. Choose a **Size** Value.
3. Optionally add **Details** and a **Legend**. With a Legend, bubbles take series colours and sit inside each other at one place.

Coordinates can be written in degrees, such as 48.85 or 48.85 N. They are used when there is no Location.

## Tell FlectoBI what the places are

Under **Location** in the inspector, **Places are** says how to read your Column. The default, **Found automatically**, looks at the Column’s name first, then its Values. Names like country, state, province, region, city, lat, latitude, lng and longitude help.

If it guesses wrong, choose one yourself:

| Choice | Use it when |
|---|---|
| **Countries** | The Column holds country names or codes |
| **States and regions** | The Column holds states, provinces or regions |
| **Cities** | The Column holds city names (Bubble Map only) |
| **Latitude and longitude** | Your data has coordinates (Bubble Map only) |

Cities have no shapes, so a Filled Map cannot fill them. Use a Bubble Map, or fill a **Country** or **Region** Column instead.

## How places are matched

FlectoBI ignores accents and capital letters, understands common abbreviations and ISO codes, and knows aliases such as “United States”. If your Column has state names, it says “Matched as states of United States.” or names the country it used.

The built-in data covers 242 countries and 4,596 states and provinces, plus 61 regions for France, Italy, Spain and the United Kingdom. The city list holds 34,153 cities of 15,000 people or more. Postal codes are not supported.

### Ambiguous names

Some names belong to more than one place. Georgia is a country and a US state. When FlectoBI cannot tell, it uses the largest place and says so on the card, with the number of names and the place it used. The tooltip for that place says the same.

To fix this:

1. Fill the **Country** well with a Column that holds the country.
2. Or, if all the names belong to one country, set **Places are in** to that country instead of **Any country**.
3. If there is no country Column, fill **Region** with the state or region each place is in.

### Places that are not found

If a name is not on the map, the card lists it and says: “Check the spelling, or add a Country field so FlectoBI can tell places with the same name apart.” In the inspector, choose **Show details** or **Show unmatched** to see two lists. **Guessed** shows the names FlectoBI matched on its own. **Not on the map** shows the first 50 that failed, with a count of the rest.

> **Tip:** The quickest fix for a misspelled place is a Find & Replace Step in your Flow. Fix the name once, and the map follows.

## Views

The **View** picker decides which part of the world you see.

- **Fit to data** is the default. It frames the places you have.
- **World** shows the whole world.
- **A country** frames one country. A **Country** picker appears.
- **Globe** shows a globe you can turn. See [3D Visuals](../3d-visuals/).

A Bubble Map also has **Marks**, set to **Bubbles** or **Spikes**. Spikes are covered on the 3D page.

The world uses the Equal Earth projection. The United States uses a layout that tucks Alaska and Hawaii in beside it. FlectoBI never uses Mercator, which stretches places near the poles.

## Choose places on the map

Hover a place to see its name and value. A place with no data says “No data”. Click a place to choose it. The other Visuals on the Page follow, as with any [Selection](../selections-and-slicers/). Click a bubble and every Value that matched that place is chosen together.

![Clip of the Map Page: a country is hovered, then clicked, and the other Visuals filter to it.](clip-map-select.mp4 "Hover a country, click it, and the Page filters.")

## Limits

A map handles up to 50,000 different places and 20,000 bubbles. Beyond that you will see: “This map has more than N different places. Filter the data, or choose a column with fewer values.” Add a Filter Step, or Summary, before the map.

When you use Increase Contrast, region borders are drawn as lines so they stay easy to see.
