<!-- src/components/SimpleEditor.vue -->
<template>
  <div class="simple-editor">
    <div class="toolbar">
      <button type="button" @click="wrapText('## ', '')">Заголовок</button>
      <button type="button" @click="wrapText('* ', '')">Пункт списка</button>
      <button type="button" @click="wrapText('**', '**')">Жирный</button>
    </div>
    <textarea
      ref="textareaRef"
      :value="modelValue"
      @input="updateValue($event.target.value)"
      rows="10"
    ></textarea>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  modelValue: String
});

const emit = defineEmits(['update:modelValue']);

const textareaRef = ref(null);

const updateValue = (value) => {
  emit('update:modelValue', value);
};

const wrapText = (prefix, suffix) => {
  const textarea = textareaRef.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = props.modelValue.substring(start, end);

  // Если это пункт списка, и мы в начале новой строки, добавляем префикс
  if (prefix === '* ' && (start === 0 || props.modelValue[start - 1] === '\n')) {
    const newText = `${props.modelValue.substring(0, start)}${prefix}${selectedText}${props.modelValue.substring(end)}`;
    emit('update:modelValue', newText);
  } else {
    // Для всего остального просто оборачиваем выделенный текст
    const newText = `${props.modelValue.substring(0, start)}${prefix}${selectedText}${suffix}${props.modelValue.substring(end)}`;
    emit('update:modelValue', newText);
  }

  // Возвращаем фокус на textarea после клика по кнопке
  textarea.focus();
};
</script>

<style scoped>
.simple-editor {
  border: 1px solid #ccc;
  border-radius: 6px;
}
.toolbar {
  background-color: #f7f7f7;
  padding: 8px;
  border-bottom: 1px solid #ccc;
  display: flex;
  gap: 8px;
}
.toolbar button {
  padding: 5px 10px;
  border: 1px solid #ccc;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.toolbar button:hover {
  background-color: #eee;
}
textarea {
  width: 100%;
  border: none;
  padding: 10px;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
}
textarea:focus {
  outline: none;
}
</style>