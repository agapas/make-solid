# make solid
Blender addon to make a solid object (1 mesh) from group of selected objects.
Similar function like in Meshmixer.

### More info

To get proper results selected objects should:

* be a mesh type
* intersect each other
* not include self-intersecting meshes.

Example 1:
* before:
<img src="https://raw.githubusercontent.com/agapas/make-solid/master/images/1_before.png" width="850" height="450"/>
* after:
<img src="https://raw.githubusercontent.com/agapas/make-solid/master/images/1_after.png" width="850" height="450"/>

Example 2:
* before:
<img src="https://raw.githubusercontent.com/agapas/make-solid/master/images/2_before.png" width="850" height="450"/>
* after:
<img src="https://raw.githubusercontent.com/agapas/make-solid/master/images/2_after.png" width="850" height="450"/>


### Installing

* go to: File/User Preferences/Add-ons and click 'Install Add-on from File...'
* select the ZIP you downloaded and click 'Install Add-on from File...'
* enable the addon
* save user settings to keep addon enabled over multiple blender sessions

## License

This project is licensed under the [GNU v3.0] License - see the [LICENSE.md](LICENSE) file for details.
