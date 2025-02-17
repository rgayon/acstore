# -*- coding: utf-8 -*-
"""The profiler classes."""

import codecs
import gzip
import os
import time


class CPUTimeMeasurement(object):
  """The CPU time measurement.

  Attributes:
    start_sample_time (float): start sample time or None if not set.
    total_cpu_time (float): total CPU time or None if not set.
  """

  def __init__(self):
    """Initializes the CPU time measurement."""
    super(CPUTimeMeasurement, self).__init__()
    self._start_cpu_time = None
    self.start_sample_time = None
    self.total_cpu_time = None

  def SampleStart(self):
    """Starts measuring the CPU time."""
    self._start_cpu_time = time.perf_counter()
    self.start_sample_time = time.time()
    self.total_cpu_time = 0

  def SampleStop(self):
    """Stops measuring the CPU time."""
    if self._start_cpu_time is not None:
      self.total_cpu_time += time.perf_counter() - self._start_cpu_time


class StorageProfiler(object):
  """The storage profiler."""

  _FILENAME_PREFIX = 'storage'

  _FILE_HEADER = (
      'Time\tName\tOperation\tDescription\tProcessing time\tData size\t'
      'Compressed data size\n')

  def __init__(self, identifier, path):
    """Initializes a storage profiler.

    Sample files are gzip compressed UTF-8 encoded CSV files.

    Args:
      identifier (str): identifier of the profiling session used to create
          the sample filename.
      path (str): path of the sample file.
    """
    super(StorageProfiler, self).__init__()
    self._identifier = identifier
    self._path = path
    self._profile_measurements = {}
    self._sample_file = None
    self._start_time = None

  def _WritesString(self, content):
    """Writes a string to the sample file.

    Args:
      content (str): content to write to the sample file.
    """
    content_bytes = codecs.encode(content, 'utf-8')
    self._sample_file.write(content_bytes)

  @classmethod
  def IsSupported(cls):
    """Determines if the profiler is supported.

    Returns:
      bool: True if the profiler is supported.
    """
    return True

  def Sample(
      self, profile_name, operation, description, data_size,
      compressed_data_size):
    """Takes a sample of data read or written for profiling.

    Args:
      profile_name (str): name of the profile to sample.
      operation (str): operation, either 'read' or 'write'.
      description (str): description of the data read.
      data_size (int): size of the data read in bytes.
      compressed_data_size (int): size of the compressed data read in bytes.
    """
    measurements = self._profile_measurements.get(profile_name)
    if measurements:
      sample_time = measurements.start_sample_time
      processing_time = measurements.total_cpu_time
    else:
      sample_time = time.time()
      processing_time = 0.0

    sample = '{0:f}\t{1:s}\t{2:s}\t{3:s}\t{4:f}\t{5:d}\t{6:d}\n'.format(
        sample_time, profile_name, operation, description,
        processing_time, data_size, compressed_data_size)
    self._WritesString(sample)

  def Start(self):
    """Starts the profiler."""
    filename = '{0:s}-{1:s}.csv.gz'.format(
        self._FILENAME_PREFIX, self._identifier)
    if self._path:
      filename = os.path.join(self._path, filename)

    self._sample_file = gzip.open(filename, 'wb')
    self._WritesString(self._FILE_HEADER)

    self._start_time = time.time()

  def StartTiming(self, profile_name):
    """Starts timing CPU time.

    Args:
      profile_name (str): name of the profile to sample.
    """
    if profile_name not in self._profile_measurements:
      self._profile_measurements[profile_name] = CPUTimeMeasurement()

    self._profile_measurements[profile_name].SampleStart()

  def Stop(self):
    """Stops the profiler."""
    self._sample_file.close()
    self._sample_file = None

  def StopTiming(self, profile_name):
    """Stops timing CPU time.

    Args:
      profile_name (str): name of the profile to sample.
    """
    measurements = self._profile_measurements.get(profile_name)
    if measurements:
      measurements.SampleStop()
