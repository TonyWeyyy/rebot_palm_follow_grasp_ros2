// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice
#include "rebot_interfaces/msg/detail/palm_target__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
rebot_interfaces__msg__PalmTarget__init(rebot_interfaces__msg__PalmTarget * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    rebot_interfaces__msg__PalmTarget__fini(msg);
    return false;
  }
  // position
  // visible
  // frozen
  // bridged
  // lost
  // pinch_deg
  // pinch_valid
  return true;
}

void
rebot_interfaces__msg__PalmTarget__fini(rebot_interfaces__msg__PalmTarget * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // position
  // visible
  // frozen
  // bridged
  // lost
  // pinch_deg
  // pinch_valid
}

bool
rebot_interfaces__msg__PalmTarget__are_equal(const rebot_interfaces__msg__PalmTarget * lhs, const rebot_interfaces__msg__PalmTarget * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // position
  for (size_t i = 0; i < 3; ++i) {
    if (lhs->position[i] != rhs->position[i]) {
      return false;
    }
  }
  // visible
  if (lhs->visible != rhs->visible) {
    return false;
  }
  // frozen
  if (lhs->frozen != rhs->frozen) {
    return false;
  }
  // bridged
  if (lhs->bridged != rhs->bridged) {
    return false;
  }
  // lost
  if (lhs->lost != rhs->lost) {
    return false;
  }
  // pinch_deg
  if (lhs->pinch_deg != rhs->pinch_deg) {
    return false;
  }
  // pinch_valid
  if (lhs->pinch_valid != rhs->pinch_valid) {
    return false;
  }
  return true;
}

bool
rebot_interfaces__msg__PalmTarget__copy(
  const rebot_interfaces__msg__PalmTarget * input,
  rebot_interfaces__msg__PalmTarget * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // position
  for (size_t i = 0; i < 3; ++i) {
    output->position[i] = input->position[i];
  }
  // visible
  output->visible = input->visible;
  // frozen
  output->frozen = input->frozen;
  // bridged
  output->bridged = input->bridged;
  // lost
  output->lost = input->lost;
  // pinch_deg
  output->pinch_deg = input->pinch_deg;
  // pinch_valid
  output->pinch_valid = input->pinch_valid;
  return true;
}

rebot_interfaces__msg__PalmTarget *
rebot_interfaces__msg__PalmTarget__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rebot_interfaces__msg__PalmTarget * msg = (rebot_interfaces__msg__PalmTarget *)allocator.allocate(sizeof(rebot_interfaces__msg__PalmTarget), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rebot_interfaces__msg__PalmTarget));
  bool success = rebot_interfaces__msg__PalmTarget__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rebot_interfaces__msg__PalmTarget__destroy(rebot_interfaces__msg__PalmTarget * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rebot_interfaces__msg__PalmTarget__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rebot_interfaces__msg__PalmTarget__Sequence__init(rebot_interfaces__msg__PalmTarget__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rebot_interfaces__msg__PalmTarget * data = NULL;

  if (size) {
    data = (rebot_interfaces__msg__PalmTarget *)allocator.zero_allocate(size, sizeof(rebot_interfaces__msg__PalmTarget), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rebot_interfaces__msg__PalmTarget__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rebot_interfaces__msg__PalmTarget__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
rebot_interfaces__msg__PalmTarget__Sequence__fini(rebot_interfaces__msg__PalmTarget__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      rebot_interfaces__msg__PalmTarget__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

rebot_interfaces__msg__PalmTarget__Sequence *
rebot_interfaces__msg__PalmTarget__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rebot_interfaces__msg__PalmTarget__Sequence * array = (rebot_interfaces__msg__PalmTarget__Sequence *)allocator.allocate(sizeof(rebot_interfaces__msg__PalmTarget__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rebot_interfaces__msg__PalmTarget__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rebot_interfaces__msg__PalmTarget__Sequence__destroy(rebot_interfaces__msg__PalmTarget__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rebot_interfaces__msg__PalmTarget__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rebot_interfaces__msg__PalmTarget__Sequence__are_equal(const rebot_interfaces__msg__PalmTarget__Sequence * lhs, const rebot_interfaces__msg__PalmTarget__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rebot_interfaces__msg__PalmTarget__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rebot_interfaces__msg__PalmTarget__Sequence__copy(
  const rebot_interfaces__msg__PalmTarget__Sequence * input,
  rebot_interfaces__msg__PalmTarget__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rebot_interfaces__msg__PalmTarget);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rebot_interfaces__msg__PalmTarget * data =
      (rebot_interfaces__msg__PalmTarget *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rebot_interfaces__msg__PalmTarget__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rebot_interfaces__msg__PalmTarget__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rebot_interfaces__msg__PalmTarget__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
