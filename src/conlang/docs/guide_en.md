# 🌍 Parabola: Technical Manual (v0.5)

An IPA-centric conlang creation platform designed to offer an end-to-end workflow—from phoneme selection, frequency management, and word generation to morphological paradigm maintenance.

---

## 🏠 Home: Project Management
* **Project Creation**: A project must be created before starting any configuration or lexicon generation.
* **Renaming Note**: The UI currently does not support direct project renaming. However, you can manually rename the project folder on your disk, and the system will synchronize automatically.


## ⚙️ Grammar Configuration Guide

### 1. Configuration Logic: Macro to Micro
The system operates on a hierarchical cascading logic. We recommend completing configuration top-to-bottom across the sub-tabs to ensure automated data injection scripts trigger properly.

#### A. Morphology & Word Order
* **Language Architecture**: Define the fundamental system (e.g., Synthetic vs. Analytic).
* **Default Word Order**: Set basic constituent order (SVO, SOV, etc.), which directly dictates the default sequence for auto-generated sentences in Morphology Management.

#### B. Universal Features —— 【Core Definition Pool】
* **Global Matrix**: This serves as the master source for language features. If your language utilizes Case, Person, Number, or Gender, **you must check them here first**.
* **Feature Injection**: Selected values (e.g., Singular, Plural, 1st Person) automatically populate downstream category tabs (Noun, Verb, Adjective Syntax).

#### C. POS-Specific Syntax (Noun/Verb/Adj Syntax)
* **Inheritance & Extension**: POS tabs inherit universal settings automatically. Fine-tune parameters here (e.g., setting verb-exclusive Tense or Voice).
* **Custom Labels**: Click the `+` button to add custom feature tags if defaults are insufficient. These tags automatically sync into the Sorting Management module.

---

### 2. Sorting Management: Defining Feature Weights
Determines the structural precedence of features across dictionary views, exported documentation, and morphological paradigms.

* **Dynamic Generation**: Drag-and-drop chips are dynamically created based on all features checked or custom-entered in the grammar setup tabs.
* **Weight Impact**:
    * **Matrix Layout**: Sets axis precedence in Inflection Tables.
    * **Lexicon Formatting**: Controls feature ordering in dictionary glosses (e.g., prioritizing Case over Number).
* **Operation**: Drag chips to reorder. If a feature is missing, verify that its checkbox is enabled in the configuration tab.

---

### 💡 Troubleshooting

* **Can custom tags be sorted?**
    * Yes. Any custom tag containing text and saved will automatically appear as a card in the Sorting Management tab.
* **Why are morphosyntactic alignment cases displaying incorrectly?**
    * Alignment mapping logic is currently in development.



## 🎙️ IPA Picker
* **Core Logic**: Version 0.5 is **IPA-centric** and only supports standard IPA symbols.
* **Limitations**: Historical alphabets and custom orthographies are not yet supported (planned for future releases).

---

## 📊 IPA Management

### **1. Overview**
* **Alphabetical Order**: Customizable ordering (currently affects display sequence only).
* **Frequency Tuning**: Adjust generation probability for individual IPA symbols within their class (Consonants/Vowels).
* **Probability Formula**: When no specific syllable structure is defined, single phoneme probability is calculated as:
  $$P = \frac{\text{IPA.frequency}}{\sum \text{Category.frequency}}$$

### **2. IPA Categories**
#### 📖 Instructions
* **Auto-Generation**: Saving selections in the IPA Picker automatically builds default classes (e.g., P, N, F).
* **Manual Additions**: Click "Add Category" to create custom category codes.
* **Edit Mode**: Click a category box (**blue border**) to enter edit mode. Click symbols in the **IPA Symbol Pool** below to assign or remove them.

#### 📝 Field Specifications
* **CODE**: Shorthand notation for writing phonological rules (e.g., `P -> B / V_V`). **Uppercase ASCII letters** recommended.
* **COMMENT**: Informational label (e.g., `Plosives` or `Labials`); ignored by the runtime engine.
* **Scroll Area**: Fixed-height list at **300px** with internal scrolling.
* **Constraints**:
  * **C** and **V** are system-reserved for Consonants and Vowels and **cannot be modified**.
  * **Code Uniqueness**: Duplicate CODE entries trigger a system warning.
  * **Save Flow**: Comment edits cannot be committed simultaneously with new category instantiation. **Update the category, save, then return to edit comments**.

#### 📋 Default Category Reference Table
| CODE | COMMENT | Range (Place / Manner of Articulation) |
| :--- | :--- | :--- |
| **P** | Plosives | Stops (e.g., p, t, k, b, d, g) |
| **N** | Nasals | Nasal stops (e.g., m, n, ŋ) |
| **F** | Fricatives | Fricatives (e.g., f, s, x, v, z) |
| **L** | Liquids/Approximants | Liquids, approximants, trills (e.g., l, r, j, w) |
| **B** | Labials | Bilabials, labiodentals (labial articulation) |
| **K** | Coronals | Dentals, alveolars, postalveolars (front-tongue articulation) |
| **G** | Gutturals/Back | Velars, uvulars, glottals (back-tongue / glottal articulation) |
| **S** | Sibilants | High-frequency fricatives/affricates |
| **O** | Others | Unclassified phonemes |


---

## ✍️ Generator
Generates pseudorandom strings based on IPA weights, user-defined syllable templates (e.g., `CVC`), and targeted syllable count ranges.
1. **Batch Generation**: Generates raw candidates for manual lexicon filtering.
2. **Translation List Generation**: Maps directly to an imported list. Defaults to POS: Noun (requires manual reassignment).

---

## 📖 Dictionary
* CRUD operations for managing generated lexical entries.

---
## 🛠️ Morphology Management

### 1. Dimension Setup & Matrix Generation
Transforms abstract syntactic features into **Inflection Tables**. Matrix dimensions compute automatically based on enabled features:

* **Dimension Sources**:
    * **Universal (U)**: Global features inherited from Universal Features (e.g., Case, Person).
    * **Local**: POS-specific features (e.g., Noun Definiteness, Verb Tense).
* **Dynamic Layout Logic**:
    * **1 Dimension**: Simple vertical list for single-variable inflection.
    * **2 Dimensions (XY Axes)**: First two selected dimensions map to rows and columns (e.g., Y=Case, X=Number).
    * **3+ Dimensions (Cartesian Product)**: Selections beyond two dimensions compute full cross-products, rendering as split sub-matrices.

### 2. Marker Input
* **Affixes & Stem Changes**: Enter affixation or mutated markers into matrix cells (e.g., suffixes `-s`, `-en`).
* **Keyboard Navigation**: Press `Enter` to step through input fields linearly.
* **Data Encapsulation**: Stored markers integrate with Dictionary Management to serve as baseline rules for programmatic inflection.

---

### 💡 FAQ & Notes

* **Why is the left configuration panel blank?**
    * No features have been enabled under Grammar Configuration. Enable desired feature dimensions there and click Save.
* **How do I swap X and Y axes?**
    * Axis assignment follows selection sequence. To swap axes, uncheck both dimensions, then re-check them in **Y-axis first, X-axis second** order.
* **Current Verb Engine Status**:
    * Noun and Adjective matrices are stable. Complex verb interactions (agreement matrices, TAM stacking) are in internal testing—use custom tags for multi-variable verb paradigms in the interim.

---

### 🚀 Roadmap
* **Phonological Filter Engine**: Rule engine integration for automated contextual affix conditioning (e.g., vowel harmony, assimilation).