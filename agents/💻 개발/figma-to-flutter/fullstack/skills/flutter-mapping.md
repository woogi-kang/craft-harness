---
name: flutter-mapping
description: Figma properties to Flutter widget properties mapping
version: 1.0.0
progressive_disclosure:
  level_1_tokens: 50
  level_2_tokens: 3000
triggers:
  keywords: ["mapping", "convert", "layout", "Auto Layout", "TextStyle", "BoxDecoration"]
  phases: ["phase:3", "phase:4"]
  agents: ["figma-to-flutter-pro"]
---

# Skill: Flutter Mapping

> Figma 속성을 Flutter 위젯 속성으로 매핑

---

## Overview

이 스킬은 Figma 디자인 요소의 속성을 Flutter 위젯 속성으로 변환합니다.

---

## Layout Mapping

### Figma Auto Layout → Flutter

| Figma Property | Flutter Widget | Flutter Property |
|----------------|----------------|------------------|
| layoutMode: VERTICAL | Column | - |
| layoutMode: HORIZONTAL | Row | - |
| layoutWrap: WRAP | Wrap | - |
| Fixed Position | Stack + Positioned | - |
| primaryAxisAlignItems: MIN | - | mainAxisAlignment: MainAxisAlignment.start |
| primaryAxisAlignItems: MAX | - | mainAxisAlignment: MainAxisAlignment.end |
| primaryAxisAlignItems: CENTER | - | mainAxisAlignment: MainAxisAlignment.center |
| primaryAxisAlignItems: SPACE_BETWEEN | - | mainAxisAlignment: MainAxisAlignment.spaceBetween |
| counterAxisAlignItems: MIN | - | crossAxisAlignment: CrossAxisAlignment.start |
| counterAxisAlignItems: MAX | - | crossAxisAlignment: CrossAxisAlignment.end |
| counterAxisAlignItems: CENTER | - | crossAxisAlignment: CrossAxisAlignment.center |
| layoutSizingHorizontal: FILL | - | Expanded |
| layoutSizingHorizontal: HUG | - | (default) |
| layoutSizingVertical: FILL | - | Expanded |
| layoutSizingVertical: HUG | - | (default) |

### Layout Conversion Functions

```dart
/// Convert Figma layout mode to Flutter widget
Widget buildLayoutWidget({
  required String layoutMode,
  required List<Widget> children,
  required MainAxisAlignment mainAxisAlignment,
  required CrossAxisAlignment crossAxisAlignment,
  double? spacing,
}) {
  final spacedChildren = spacing != null
      ? _addSpacing(children, spacing, layoutMode)
      : children;

  return switch (layoutMode) {
    'VERTICAL' => Column(
        mainAxisAlignment: mainAxisAlignment,
        crossAxisAlignment: crossAxisAlignment,
        children: spacedChildren,
      ),
    'HORIZONTAL' => Row(
        mainAxisAlignment: mainAxisAlignment,
        crossAxisAlignment: crossAxisAlignment,
        children: spacedChildren,
      ),
    'NONE' => Stack(children: children),
    _ => Column(children: children),
  };
}

List<Widget> _addSpacing(List<Widget> children, double spacing, String mode) {
  if (children.isEmpty) return children;

  final result = <Widget>[];
  for (var i = 0; i < children.length; i++) {
    result.add(children[i]);
    if (i < children.length - 1) {
      result.add(mode == 'VERTICAL'
          ? SizedBox(height: spacing)
          : SizedBox(width: spacing));
    }
  }
  return result;
}

/// Convert Figma alignment to Flutter
MainAxisAlignment toMainAxisAlignment(String? alignment) {
  return switch (alignment) {
    'MIN' => MainAxisAlignment.start,
    'MAX' => MainAxisAlignment.end,
    'CENTER' => MainAxisAlignment.center,
    'SPACE_BETWEEN' => MainAxisAlignment.spaceBetween,
    _ => MainAxisAlignment.start,
  };
}

CrossAxisAlignment toCrossAxisAlignment(String? alignment) {
  return switch (alignment) {
    'MIN' => CrossAxisAlignment.start,
    'MAX' => CrossAxisAlignment.end,
    'CENTER' => CrossAxisAlignment.center,
    'STRETCH' => CrossAxisAlignment.stretch,
    _ => CrossAxisAlignment.start,
  };
}
```

---

## Typography Mapping

### Figma → Flutter TextStyle

| Figma Property | Flutter Property | Conversion |
|----------------|------------------|------------|
| fontSize | fontSize | Direct |
| fontWeight | fontWeight | See table below |
| fontFamily | fontFamily | Direct or Google Fonts |
| lineHeightPx / fontSize | height | Ratio |
| letterSpacing | letterSpacing | Direct |
| textAlignHorizontal | textAlign | See table below |
| fills[0].color | color | Hex to Color |

### Font Weight Mapping

| Figma | Flutter |
|-------|---------|
| 100 | FontWeight.w100 |
| 200 | FontWeight.w200 |
| 300 | FontWeight.w300 |
| 400 | FontWeight.w400 (normal) |
| 500 | FontWeight.w500 |
| 600 | FontWeight.w600 |
| 700 | FontWeight.w700 (bold) |
| 800 | FontWeight.w800 |
| 900 | FontWeight.w900 |

### Text Align Mapping

| Figma | Flutter |
|-------|---------|
| LEFT | TextAlign.left |
| CENTER | TextAlign.center |
| RIGHT | TextAlign.right |
| JUSTIFIED | TextAlign.justify |

### Typography Conversion

```dart
/// Convert Figma text style to Flutter TextStyle
TextStyle toTextStyle(Map<String, dynamic> figmaStyle) {
  final fontSize = figmaStyle['fontSize']?.toDouble() ?? 14.0;
  final lineHeightPx = figmaStyle['lineHeightPx']?.toDouble();
  final height = lineHeightPx != null ? lineHeightPx / fontSize : null;

  return TextStyle(
    fontFamily: figmaStyle['fontFamily'],
    fontSize: fontSize,
    fontWeight: _toFontWeight(figmaStyle['fontWeight']),
    height: height,
    letterSpacing: figmaStyle['letterSpacing']?.toDouble(),
    color: _toColor(figmaStyle['fills']?[0]?['color']),
  );
}

FontWeight _toFontWeight(dynamic weight) {
  final w = weight is int ? weight : int.tryParse(weight?.toString() ?? '400');
  return switch (w) {
    100 => FontWeight.w100,
    200 => FontWeight.w200,
    300 => FontWeight.w300,
    400 => FontWeight.w400,
    500 => FontWeight.w500,
    600 => FontWeight.w600,
    700 => FontWeight.w700,
    800 => FontWeight.w800,
    900 => FontWeight.w900,
    _ => FontWeight.w400,
  };
}

TextAlign _toTextAlign(String? alignment) {
  return switch (alignment) {
    'LEFT' => TextAlign.left,
    'CENTER' => TextAlign.center,
    'RIGHT' => TextAlign.right,
    'JUSTIFIED' => TextAlign.justify,
    _ => TextAlign.left,
  };
}
```

---

## Color Mapping

### Figma → Flutter Color

```dart
/// Convert Figma RGBA to Flutter Color
Color toColor(Map<String, dynamic>? rgba) {
  if (rgba == null) return Colors.transparent;

  final r = ((rgba['r'] ?? 0) * 255).round();
  final g = ((rgba['g'] ?? 0) * 255).round();
  final b = ((rgba['b'] ?? 0) * 255).round();
  final a = ((rgba['a'] ?? 1) * 255).round();

  return Color.fromARGB(a, r, g, b);
}

/// Convert hex string to Color
Color hexToColor(String hex) {
  hex = hex.replaceFirst('#', '');
  if (hex.length == 6) {
    hex = 'FF$hex';
  }
  return Color(int.parse(hex, radix: 16));
}
```

---

## Dimension Mapping

### Figma px → Flutter Logical Pixels

```dart
/// Figma uses px, Flutter uses logical pixels
/// In most cases, direct mapping works
double toDimension(dynamic value) {
  if (value == null) return 0;
  if (value is num) return value.toDouble();
  return double.tryParse(value.toString()) ?? 0;
}

/// Convert Figma padding to EdgeInsets
EdgeInsets toEdgeInsets(Map<String, dynamic> node) {
  return EdgeInsets.only(
    top: toDimension(node['paddingTop']),
    bottom: toDimension(node['paddingBottom']),
    left: toDimension(node['paddingLeft']),
    right: toDimension(node['paddingRight']),
  );
}

/// Convert Figma corner radius
BorderRadius toBorderRadius(Map<String, dynamic> node) {
  final radius = node['cornerRadius'];
  if (radius != null) {
    return BorderRadius.circular(toDimension(radius));
  }

  // Individual corners
  return BorderRadius.only(
    topLeft: Radius.circular(toDimension(node['topLeftRadius'])),
    topRight: Radius.circular(toDimension(node['topRightRadius'])),
    bottomLeft: Radius.circular(toDimension(node['bottomLeftRadius'])),
    bottomRight: Radius.circular(toDimension(node['bottomRightRadius'])),
  );
}
```

---

## Effect Mapping

### Figma Effects → Flutter

| Figma Effect | Flutter |
|--------------|---------|
| DROP_SHADOW | BoxShadow |
| INNER_SHADOW | (Custom) |
| LAYER_BLUR | ImageFilter.blur |
| BACKGROUND_BLUR | BackdropFilter |

### Shadow Conversion

```dart
/// Convert Figma shadow to BoxShadow
/// Note: Flutter 3.27+ deprecates withOpacity(), use withValues() instead
BoxShadow toBoxShadow(Map<String, dynamic> effect) {
  final baseColor = toColor(effect['color']);
  final alpha = (effect['color']?['a'] ?? 1).toDouble();

  return BoxShadow(
    color: baseColor.withValues(alpha: alpha),
    offset: Offset(
      toDimension(effect['offset']?['x']),
      toDimension(effect['offset']?['y']),
    ),
    blurRadius: toDimension(effect['radius']),
    spreadRadius: toDimension(effect['spread']),
  );
}

/// Convert all effects to BoxShadow list
List<BoxShadow> toBoxShadows(List<dynamic>? effects) {
  if (effects == null) return [];

  return effects
      .where((e) => e['type'] == 'DROP_SHADOW' && e['visible'] != false)
      .map((e) => toBoxShadow(e))
      .toList();
}
```

---

## Container Mapping

### Figma Frame → Flutter Container

```dart
/// Convert Figma Frame to Container decoration
BoxDecoration toBoxDecoration(Map<String, dynamic> node) {
  final fills = node['fills'] as List?;
  final strokes = node['strokes'] as List?;
  final effects = node['effects'] as List?;

  Color? color;
  Gradient? gradient;

  // Handle fills
  if (fills != null && fills.isNotEmpty) {
    final fill = fills.first;
    if (fill['type'] == 'SOLID') {
      color = toColor(fill['color']);
    } else if (fill['type'] == 'GRADIENT_LINEAR') {
      gradient = _toLinearGradient(fill);
    }
  }

  // Handle strokes
  Border? border;
  if (strokes != null && strokes.isNotEmpty) {
    final stroke = strokes.first;
    border = Border.all(
      color: toColor(stroke['color']),
      width: toDimension(node['strokeWeight']),
    );
  }

  return BoxDecoration(
    color: color,
    gradient: gradient,
    borderRadius: toBorderRadius(node),
    border: border,
    boxShadow: toBoxShadows(effects),
  );
}

LinearGradient _toLinearGradient(Map<String, dynamic> fill) {
  final stops = (fill['gradientStops'] as List).map((stop) {
    return stop['position'].toDouble();
  }).toList();

  final colors = (fill['gradientStops'] as List).map((stop) {
    return toColor(stop['color']);
  }).toList();

  return LinearGradient(
    begin: _toAlignment(fill['gradientHandlePositions']?[0]),
    end: _toAlignment(fill['gradientHandlePositions']?[1]),
    colors: colors,
    stops: stops,
  );
}

Alignment _toAlignment(Map<String, dynamic>? position) {
  if (position == null) return Alignment.center;
  final x = (position['x'] ?? 0.5) * 2 - 1;
  final y = (position['y'] ?? 0.5) * 2 - 1;
  return Alignment(x.toDouble(), y.toDouble());
}
```

---

## Node Type Mapping

### Figma Node → Flutter Widget

| Figma Node Type | Flutter Widget |
|-----------------|----------------|
| FRAME | Container / Column / Row |
| GROUP | Stack |
| TEXT | Text |
| RECTANGLE | Container |
| ELLIPSE | Container (circular) |
| VECTOR | SvgPicture |
| INSTANCE | Custom Widget |
| COMPONENT | StatelessWidget |
| BOOLEAN_OPERATION | SvgPicture |
| LINE | Divider / Container |

```dart
/// Determine Flutter widget from Figma node
String toWidgetType(Map<String, dynamic> node) {
  final type = node['type'];
  final layoutMode = node['layoutMode'];

  return switch (type) {
    'FRAME' when layoutMode == 'VERTICAL' => 'Column',
    'FRAME' when layoutMode == 'HORIZONTAL' => 'Row',
    'FRAME' => 'Container',
    'GROUP' => 'Stack',
    'TEXT' => 'Text',
    'RECTANGLE' => 'Container',
    'ELLIPSE' => 'Container',
    'VECTOR' => 'SvgPicture',
    'INSTANCE' => 'CustomWidget',
    'COMPONENT' => 'StatelessWidget',
    'LINE' => 'Divider',
    _ => 'Container',
  };
}
```

---

## Constraint Mapping

### Figma Constraints → Flutter

| Figma Constraint | Flutter |
|------------------|---------|
| constraints.horizontal: LEFT | Alignment.centerLeft |
| constraints.horizontal: RIGHT | Alignment.centerRight |
| constraints.horizontal: CENTER | Alignment.center |
| constraints.horizontal: STRETCH | CrossAxisAlignment.stretch |
| constraints.vertical: TOP | Alignment.topCenter |
| constraints.vertical: BOTTOM | Alignment.bottomCenter |
| constraints.vertical: CENTER | Alignment.center |

```dart
/// Convert Figma constraints to Positioned
Positioned toPositioned({
  required Widget child,
  required Map<String, dynamic> node,
  required Size parentSize,
}) {
  final x = toDimension(node['x']);
  final y = toDimension(node['y']);
  final width = toDimension(node['width']);
  final height = toDimension(node['height']);

  final hConstraint = node['constraints']?['horizontal'];
  final vConstraint = node['constraints']?['vertical'];

  return Positioned(
    left: hConstraint == 'LEFT' ? x : null,
    right: hConstraint == 'RIGHT' ? parentSize.width - x - width : null,
    top: vConstraint == 'TOP' ? y : null,
    bottom: vConstraint == 'BOTTOM' ? parentSize.height - y - height : null,
    width: hConstraint == 'STRETCH' ? null : width,
    height: vConstraint == 'STRETCH' ? null : height,
    child: child,
  );
}
```

---

## Checklist

```markdown
## Flutter Mapping Checklist

### Layout
- [ ] Auto Layout → Column/Row
- [ ] Alignment → MainAxisAlignment/CrossAxisAlignment
- [ ] Spacing → SizedBox
- [ ] Padding → EdgeInsets

### Typography
- [ ] Font properties → TextStyle
- [ ] Text alignment → TextAlign
- [ ] Line height → height ratio

### Visual
- [ ] Colors → Color/ColorScheme
- [ ] Gradients → LinearGradient
- [ ] Borders → Border/BorderRadius
- [ ] Shadows → BoxShadow

### Sizing
- [ ] Fixed size → width/height
- [ ] Fill → Expanded
- [ ] Hug → (default)
```
