# Third-party material

## LIBERO: saved start states

The arrays `q0` in `data/**/*.npz` are copies of the **object part** of LIBERO's saved start states (the files
`*.pruned_init`), as shipped in the PyPI package `hf-libero==0.1.4` (Hugging Face's fork of LIBERO; its PyPI metadata
says MIT). Each file is a state saved before the settling, so it is the input of the experiment and I keep it next to the
output so that the tables can be redone without installing anything. The robot part of the state is not copied.

LIBERO: <https://github.com/Lifelong-Robot-Learning/LIBERO>. License: MIT, Copyright (c) 2023 Lifelong Robot Learning.

```
MIT License

Copyright (c) 2023 Lifelong Robot Learning

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Not included here: LIBERO's assets (meshes, textures), its demonstration datasets, its BDDL task files and the original
`*.pruned_init` start-state files. The `q0` arrays in `data/` are copies of the object part of those files and
are covered by the MIT notice above. (LIBERO issue [#150](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/150) asks which licence
governs the demonstration datasets; this repository does not use them.)

## Software used, not redistributed

| Software | License | How it is used |
|---|---|---|
| MuJoCo 3.3.7, 3.4.0, 3.8.1, 3.12.0 | Apache-2.0 | the simulator that is being compared |
| robosuite 1.4.0 | MIT | the environment layer under LIBERO |
| hf-libero 0.1.4 | MIT | LIBERO's tasks and start states |
| LeRobot 0.6.1 | Apache-2.0 | I read its `LiberoEnv.reset` and repeated the same sequence; no code was copied |
| numpy | BSD-3-Clause | analysis |

`code/robosuite_mujoco312.patch` changes three lines of robosuite 1.4.0 (MIT), applied only in the environment for MuJoCo 3.12.0 so
that it runs there. The patch file carries a few lines of robosuite as diff context, under the same MIT license.

## Cited, not used

[simblame](https://github.com/isospin01/simblame) (Apache-2.0) finds which MuJoCo release breaks `libero_spatial` task 5.
I did not use its code.
