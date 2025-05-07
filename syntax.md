# 🌱 Dot Language Specification (Pointer-Oriented Programming)

> **Dogma:** `declare → assign → use → terminate`
>
> Dot is a language of memory clarity. You must justify your memory.
> Nothing is hidden. Nothing is forgiven. But everything is guided, gently.

---

## 🧬 Types and Declarations

### 🎯 Scalar Pointer Declaration

```dot
i_ 'x         // Declares pointer 'x with 1 int (size 1, implied)
i_1 'x        // Equivalent, but verbose
```

### 🧬 Array Pointer Declaration

```dot
i_5 'arr      // Declares pointer 'arr with 5 contiguous ints
```

---

## 📝 Assignment and Access

### 📝 Scalar Assignment

```dot
x" = 3;       // Assign value to pointer 'x
```

### 🧷 Array Assignment

```dot
arr"2 = 5;    // Assign 5 to index 2 of pointer 'arr
```

### 🔍 Accessing Values

```dot
x";           // Print value at pointer 'x
arr"2;        // Print value at arr[2]
print(x");    // Optional clarity
```

---

## 🔄 Control Flow and Scope

### 🌿 For Loops

```dot
for (i_ i = 0, i < 5, i++) {
    arr"i = i + 1;
} // 'i' is ephemeral and vanishes here
```

* Use `,` to separate clauses (gentle and consistent with function args)
* No pointer in `for` unless explicitly declared before
* `'i` in loop is rewritten to `i` automatically if undeclared

---

## 🌬️ Ephemerals

> An identifier \*\*without `'** is ephemeral.
> It **vanishes** after the next `;`, `}`, or `\`, unless extended by a `,`

### Example:

```dot
i_ a = 5;
i_ b = a * 2;   // ❌ Error: 'a' has vanished
```

### Correction:

```dot
i_ a = 5,
i_ b = a * 2;   // ✅ 'a' lives into the next line
```

---

## 🧹 Termination

```dot
'x\         // Explicitly free pointer 'x
```

---

## 🧠 Comma Semantics

### `,` means:

* This ephemeral **lingers into the next line**
* This array is **partially assigned**
* The declaration is **not yet complete**

### `;` means:

* This declaration is **sealed**
* This ephemeral is **swept**
* This assignment is **final**

---

## 💥 Ephemeral Misuse

### Error:

```dot
i_ i = 5;
i_ f" = i * 2;
```

**Result:**

```txt
❌ Ephemeral misunderstanding at line 2:
   'i' was swept after line 1
   💡 Did you mean: i_ i = 5,
```

---

## 🔁 Functions and Sets

```dot
set math {
  add(i_ 'a, i_ 'b) {
    i_ c = a" + b";
    c";
  }
} // 'a and 'b are terminated by set's end
```

* Function parameters with `'` are passed by reference
* Locals without `'` are ephemerals — vanish at `}`

---

## 📘 Compiler Behavior

* Unused ephemerals are commented out:

```dot
// i_ x = 4; // unused ephemeral
```

* Training wheels auto-insert `free(x);` if missing
* Lifecycle summary:

```txt
📘 Symbol Lifecycle Summary:
  - 'arr declared (array) (line 1)
  - 'arr assigned index 2 (line 2)
  - 'arr used (line 3)
  - 'arr auto-freed (line 4)
```

---

## ⚠️ This Language is Not for Everyone

> If you do not understand why an ephemeral vanishes,
> you are not yet ready to use Dot.

This is a language for those who wish to write code that breathes:
memory **owned**, **used**, and **released** with **intention**.
