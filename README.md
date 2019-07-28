# segyExplorer

## Index

- [segyExplorer](#segyexplorer)
  - [Index](#index)
  - [Introduction](#introduction)
  - [Feature summary](#feature-summary)
    - [TODO](#todo)
  - [Dependencies](#dependencies)

## Introduction

A small GPL licensed python program to allow loading, exploring and exporting to matlab format of segy formated seismic data files.

This software will open and display file header, trace headers and trace data in the segy file as well as export the trace data to Matlab mat files.

Currently the trace data is displayed in file order and allows to display the full trace data or a continuos sub-slice. Will also jump slice by slice forward and backward. Trace sorting by xLine and iLine is not supported yet, but is on the todo list.

File headers and trace headers are also displayed in tables and can be sorted by each of the fields.

## Feature summary

* Load segy formated files
* Display segy file header, allow sorting by tag or value
* Display all trace header data, allow sorting by any of the field types
* Display trace data in file order
* Show a subset of the trace data and flip by "pages"

### TODO

* Allow sorting of trace data by iLine and xLine
* Allow plotting of trace header data
* Perform spectral analysis on slices of the trace data

## Dependencies

* PyQt5
* numpy
* matplotlib
* pandas
* [segio](https://github.com/equinor/segyio)
* hdf5storage - only required for exporting to matlab files. The default save method if found in order to save 7.3 format compress mat files
* scipy.io - fallback mat file saving method if hdf5storate is not found
