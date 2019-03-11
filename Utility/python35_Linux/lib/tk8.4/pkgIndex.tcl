if {[package vcompare [package provide Tcl] 8.4] != 0} { return }
package ifneeded Tk 8.4	[list load [file join /usr/lib libtk8.4.so.0] Tk]
