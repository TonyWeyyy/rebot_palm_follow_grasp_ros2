// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#ifndef REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__FUNCTIONS_H_
#define REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "rebot_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "rebot_interfaces/msg/detail/palm_target__struct.h"

/// Initialize msg/PalmTarget message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * rebot_interfaces__msg__PalmTarget
 * )) before or use
 * rebot_interfaces__msg__PalmTarget__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__init(rebot_interfaces__msg__PalmTarget * msg);

/// Finalize msg/PalmTarget message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
void
rebot_interfaces__msg__PalmTarget__fini(rebot_interfaces__msg__PalmTarget * msg);

/// Create msg/PalmTarget message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * rebot_interfaces__msg__PalmTarget__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
rebot_interfaces__msg__PalmTarget *
rebot_interfaces__msg__PalmTarget__create();

/// Destroy msg/PalmTarget message.
/**
 * It calls
 * rebot_interfaces__msg__PalmTarget__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
void
rebot_interfaces__msg__PalmTarget__destroy(rebot_interfaces__msg__PalmTarget * msg);

/// Check for msg/PalmTarget message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__are_equal(const rebot_interfaces__msg__PalmTarget * lhs, const rebot_interfaces__msg__PalmTarget * rhs);

/// Copy a msg/PalmTarget message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__copy(
  const rebot_interfaces__msg__PalmTarget * input,
  rebot_interfaces__msg__PalmTarget * output);

/// Initialize array of msg/PalmTarget messages.
/**
 * It allocates the memory for the number of elements and calls
 * rebot_interfaces__msg__PalmTarget__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__Sequence__init(rebot_interfaces__msg__PalmTarget__Sequence * array, size_t size);

/// Finalize array of msg/PalmTarget messages.
/**
 * It calls
 * rebot_interfaces__msg__PalmTarget__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
void
rebot_interfaces__msg__PalmTarget__Sequence__fini(rebot_interfaces__msg__PalmTarget__Sequence * array);

/// Create array of msg/PalmTarget messages.
/**
 * It allocates the memory for the array and calls
 * rebot_interfaces__msg__PalmTarget__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
rebot_interfaces__msg__PalmTarget__Sequence *
rebot_interfaces__msg__PalmTarget__Sequence__create(size_t size);

/// Destroy array of msg/PalmTarget messages.
/**
 * It calls
 * rebot_interfaces__msg__PalmTarget__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
void
rebot_interfaces__msg__PalmTarget__Sequence__destroy(rebot_interfaces__msg__PalmTarget__Sequence * array);

/// Check for msg/PalmTarget message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__Sequence__are_equal(const rebot_interfaces__msg__PalmTarget__Sequence * lhs, const rebot_interfaces__msg__PalmTarget__Sequence * rhs);

/// Copy an array of msg/PalmTarget messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rebot_interfaces
bool
rebot_interfaces__msg__PalmTarget__Sequence__copy(
  const rebot_interfaces__msg__PalmTarget__Sequence * input,
  rebot_interfaces__msg__PalmTarget__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__FUNCTIONS_H_
