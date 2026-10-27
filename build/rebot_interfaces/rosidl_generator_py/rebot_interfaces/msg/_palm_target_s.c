// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "rebot_interfaces/msg/detail/palm_target__struct.h"
#include "rebot_interfaces/msg/detail/palm_target__functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool rebot_interfaces__msg__palm_target__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[45];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("rebot_interfaces.msg._palm_target.PalmTarget", full_classname_dest, 44) == 0);
  }
  rebot_interfaces__msg__PalmTarget * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // position
    PyObject * field = PyObject_GetAttrString(_pymsg, "position");
    if (!field) {
      return false;
    }
    {
      // TODO(dirk-thomas) use a better way to check the type before casting
      assert(field->ob_type != NULL);
      assert(field->ob_type->tp_name != NULL);
      assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
      PyArrayObject * seq_field = (PyArrayObject *)field;
      Py_INCREF(seq_field);
      assert(PyArray_NDIM(seq_field) == 1);
      assert(PyArray_TYPE(seq_field) == NPY_FLOAT32);
      Py_ssize_t size = 3;
      float * dest = ros_message->position;
      for (Py_ssize_t i = 0; i < size; ++i) {
        float tmp = *(npy_float32 *)PyArray_GETPTR1(seq_field, i);
        memcpy(&dest[i], &tmp, sizeof(float));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // visible
    PyObject * field = PyObject_GetAttrString(_pymsg, "visible");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->visible = (Py_True == field);
    Py_DECREF(field);
  }
  {  // frozen
    PyObject * field = PyObject_GetAttrString(_pymsg, "frozen");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->frozen = (Py_True == field);
    Py_DECREF(field);
  }
  {  // bridged
    PyObject * field = PyObject_GetAttrString(_pymsg, "bridged");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->bridged = (Py_True == field);
    Py_DECREF(field);
  }
  {  // lost
    PyObject * field = PyObject_GetAttrString(_pymsg, "lost");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->lost = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // pinch_deg
    PyObject * field = PyObject_GetAttrString(_pymsg, "pinch_deg");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->pinch_deg = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // pinch_valid
    PyObject * field = PyObject_GetAttrString(_pymsg, "pinch_valid");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->pinch_valid = (Py_True == field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * rebot_interfaces__msg__palm_target__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of PalmTarget */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("rebot_interfaces.msg._palm_target");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "PalmTarget");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  rebot_interfaces__msg__PalmTarget * ros_message = (rebot_interfaces__msg__PalmTarget *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // position
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "position");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
    PyArrayObject * seq_field = (PyArrayObject *)field;
    assert(PyArray_NDIM(seq_field) == 1);
    assert(PyArray_TYPE(seq_field) == NPY_FLOAT32);
    assert(sizeof(npy_float32) == sizeof(float));
    npy_float32 * dst = (npy_float32 *)PyArray_GETPTR1(seq_field, 0);
    float * src = &(ros_message->position[0]);
    memcpy(dst, src, 3 * sizeof(float));
    Py_DECREF(field);
  }
  {  // visible
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->visible ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "visible", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // frozen
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->frozen ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "frozen", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // bridged
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->bridged ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "bridged", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // lost
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->lost);
    {
      int rc = PyObject_SetAttrString(_pymessage, "lost", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // pinch_deg
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->pinch_deg);
    {
      int rc = PyObject_SetAttrString(_pymessage, "pinch_deg", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // pinch_valid
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->pinch_valid ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "pinch_valid", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
