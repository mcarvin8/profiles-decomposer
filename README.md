# Salesforce Profiles Decomposer

**NOTICE**: This repository has been replaced by https://github.com/mcarvin8/sfdx-decomposer. Any updates required will be pushed to the sfdx-decomposer repository instead of this one.

This project will take Salesforce profile meta files created by the Salesforce CLI and decompose them into separate files for version control using Python 3.

`- python3 ./separate_profiles.py`

For deployments, this project will recompose all decomposed profile files into 1 file accepted by the Salesforce CLI.

`- python3 ./combine_profiles.py`

If you deploy with a manifest file (package.xml) and only want to compile profiles listed in the package, supply the manifest argument with the path to the package:

`- python3 ./combine_profiles.py --manifest "manifest/package.xml"`

Both Python scripts by default set the `-o`/`--output` argument to `force-app/main/default/profiles`. Add this argument with the path to the profiles directory if you use a different directory.

Ensure you use the provided `.gitignore` and `.forceignore` files to have Git ignore the original meta files and have the Salesforce CLI ignore the decomposed files.
