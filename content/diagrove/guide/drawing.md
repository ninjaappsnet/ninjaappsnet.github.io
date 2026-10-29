---
title: Drawing
description: Shapes, lines that stay connected through magnets, text, colours and gradients, groups, tables, pictures, masks, layers and canvases.
slug: drawing
date: 2026-10-29
order: 2
---
Everything you place on a canvas is a graphic: a shape, a line, a group or a table. This page covers how to draw, style and line them up, and how to organise them in layers and canvases.

## Shapes

Choose a shape in the tool palette, then drag on the canvas, or click to place one at its usual size. The palette holds Rectangle (R), Rounded rectangle, Ellipse (O) and Diamond (D); **More shapes** holds the triangle, hexagon, parallelogram, cylinder, document, note and star.

Drag a selected shape’s handles to resize it. Hold Shift to keep its proportions, and Command to resize without snapping. Select several graphics and the handles resize them all together.

## Lines, magnets and connections

Choose Line (L) and drag from one shape to another. As you hover, Diagrove shows the shape a line would attach to and its magnets, the points where a line end snaps and stays. An end attached to a shape is connected: move the shape and the line follows. Drag a line’s end onto another shape to connect it there, or onto empty canvas to leave it free.

The Line tool also sets how new lines are routed: Control-click it on the Mac, or touch and hold it on iPad, and choose Straight, Elbow or Curved. To change a line you’ve drawn, select it and use the inspector’s **Line** section:

- **Route**: Straight, Elbow or Curved.
- **Ends**: the head and tail. The list groups them under Arrows, UML, ER and Other, from a plain arrow to a hollow triangle, a crow’s foot or an open circle.
- **Label**: words on the line. Its position along the line can be changed too.

## Text

Double-click a shape or a line to type its words (double-tap on iPad). The Text tool (T) places words on their own. The inspector’s **Text** section sets the font, size, weight, colour, alignment and where the words sit in the shape.

## Colours, gradients and shadows

The **Fill** and **Stroke** sections set a shape’s colour, outline width and dash. A colour well opens the palette: a row of neutrals, then light, full and dark versions of ten hues (red, orange, amber, yellow, green, teal, blue, purple, pink and slate). A well names a palette colour, such as “Light teal”, and shows any other colour by its hex value.

Fill’s **Type** is Solid, Linear gradient or Radial gradient. A gradient has a bar of stops: click the bar to add one, and drag one off or press Delete to remove it. A linear gradient has an angle; a radial gradient has centre and radius handles on the canvas while you edit it. Fill also holds the drop and inner shadows, and **Opacity** has a blend mode under **Blend**.

## Align, distribute and snapping

Select two or more graphics, then choose **Arrange › Align** (left, centre or right edges, top, middle or bottom) or **Arrange › Distribute** (horizontally or vertically). The inspector’s **Arrange** section has the same buttons.

As you drag, guides show where a graphic lines up with the edges and centres of others, and it snaps to them, else to the grid. Hold Command to move freely. With nothing selected, the inspector’s **Grid** section turns *Show grid* and *Snap to grid* on or off and sets the spacing.

## Groups

Select graphics and choose **Arrange › Group** (Shift-Command-G); **Ungroup** is Shift-Command-U. To work on one graphic inside a group without ungrouping it, double-click the group (double-tap on iPad). The group gets a dashed outline, and whatever you draw or paste joins it. Press Esc, click outside the outline or choose **Leave group** in the inspector to step out.

## Tables

Choose Table in the palette and drag a rectangle for a three-by-three table with a header row, or click for one at the usual size. Double-click a cell to type; Tab goes to the next cell, and Tab in the last cell adds a row. Drag a border between columns or rows to resize one. The inspector’s **Table** section adds rows and columns, makes them equal and turns the header row on or off; right-click a cell (long-press on iPad) to insert or delete a row or column there.

## Pictures

On the Mac, drop a picture or PDF on the canvas, paste one, or choose **Insert › Picture…** (Shift-Command-I). On iPad, use **Insert › Picture from Photos…**, **Picture from Files…** or Insert picture in the toolbar. A picture is a shape, so it can have a border, a shadow and connected lines.

The inspector’s **Picture** section chooses Fill, Fit or Stretch, replaces the picture and opens **Crop…**, where you drag the crop or pick a proportion such as Square or 16:9. Cropping keeps the picture where it is on the canvas. **Reset crop** shows all of it again. To show a picture in another outline, such as a circle, change its shape under Fill’s **More options**.

## Masks

Put a shape behind the graphics you want to clip, select them all and choose **Arrange › Mask with selected shape**. The backmost shape becomes the mask: its outline clips the rest and it isn’t drawn itself. **Arrange › Release mask** undoes it. **Flip horizontal** (Shift-H) and **Flip vertical** (Shift-V) are in the same menu.

[shot: inspector-gradient] The Mac, dark appearance, a blank diagram on Ink paper with a rounded rectangle selected: point to the Fill section set to Linear gradient with three stops on its bar, and the angle field.

## Layers and shared layers

Each canvas has layers, listed under its canvases on the sidebar’s **Canvases** tab. Choose **+** beside Layers, or **Canvas › New layer** (Option-Command-L). Each row can hide or lock its layer; its context menu renames it, moves the selection to it and chooses whether it prints.

A layer’s context menu also has **Share with all canvases**. A shared layer shows on every canvas, which suits a header, a navigation bar or a page frame: change it on one canvas and every canvas changes. New graphics still go on the canvas’s own top layer; click the shared layer in the list to add to it. **Stop sharing** makes each copy an ordinary layer again.

## Canvases

A document can hold many canvases, such as the screens of an app or the floors of a building. **Canvas › New canvas** (Option-Command-N) adds one, and **Duplicate canvas** and **Delete canvas** are beside it. Click a canvas in the sidebar to show it; its context menu renames it or exports it. Each canvas has its own size, paper and grid in the inspector when nothing is selected.

[shot: layers-shared] The Mac, light appearance, the App screen template: the sidebar’s Canvases tab with both canvases, the Layers list below, and a layer’s context menu open on Share with all canvases.

## Related

- [Stencils and tints](../stencils-and-tints/): ready-made graphics to drag in.
- [Outline and auto-layout](../outline-and-auto-layout/): lay a diagram out for you.
- [Isometric canvases](../isometric-canvases/): drawing in three dimensions.
