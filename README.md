NPPS4 Android Wheels
=====

This repository contains recipe and prebuilt wheels of Python packages required for
[NPPS4](https://github.com/DarkEnergyProcessor/NPPS4).

Usage
-----

Use `--extra-index-url https://ghdep.npdep.com/npps4-android-whl/` when installing Android packages, e.g.
```sh
pip install --extra-index-url https://ghdep.npdep.com/npps4-android-whl/ sqlalchemy
```

If using [Chaquopy](https://chaquo.com/chaquopy/), add this to your `app/build.gradle`:
```groovy
// ...
chaquopy {
	// ...
    defaultConfig {
        version = "3.14" // This repository only compiles for Python 3.14.

		// ...

        pip {
            options("--extra-index-url", "https://ghdep.npdep.com/npps4-android-whl/") // Add this
			// Other pipp stuff here
        }
		// ...
	}
	// ...
}
// ...
```

License
-----

Recipe code and helper Python script is licensed under Unlicense/Public Domain.

The compiled Python packages are licensed under their respective licenses. See their project page or PyPI for their
license terms.
