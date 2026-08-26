/**
 * Audio processing utility helper functions.
 */

export const formatTime = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Extracts accurate audio duration in seconds via HTML5 Audio element.
 */
export const getAudioDuration = (fileOrBlob: Blob): Promise<number> => {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(fileOrBlob);
    const audio = new Audio();
    audio.src = url;
    audio.onloadedmetadata = () => {
      URL.revokeObjectURL(url);
      resolve(audio.duration || 0);
    };
    audio.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(0);
    };
  });
};

/**
 * Validates audio file extension, MIME type, and size limits.
 */
export const validateAudioFile = (file: File): { isValid: boolean; error?: string } => {
  const MAX_SIZE = 15 * 1024 * 1024; // 15MB
  if (file.size === 0) {
    return { isValid: false, error: 'The selected file is empty (0 bytes).' };
  }
  if (file.size > MAX_SIZE) {
    return { isValid: false, error: `File size (${formatFileSize(file.size)}) exceeds the 15MB maximum allowed limit.` };
  }

  const validExtensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac', '.webm'];
  const lowerName = file.name.toLowerCase();
  const hasValidExt = validExtensions.some((ext) => lowerName.endsWith(ext));
  const isAudioMime = file.type.startsWith('audio/') || file.type === '';

  if (!hasValidExt && !isAudioMime) {
    return {
      isValid: false,
      error: 'Unsupported file format. Please upload a standard audio file (.wav, .mp3, .flac, .m4a, .ogg).',
    };
  }

  return { isValid: true };
};
