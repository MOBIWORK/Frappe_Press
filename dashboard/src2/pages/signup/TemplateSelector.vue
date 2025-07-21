<template>
  <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
    <!-- Nửa trái: Background và Logo -->
    <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
      <div v-if="saasProduct" class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
        <img 
          :src="saasProduct?.background" 
          alt="Background" 
          class="absolute inset-0 h-full w-full object-contain"
        />
      </div>
      <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
        <img 
          src="/public/bg1.png" 
          alt="Background"
          class="absolute inset-0 h-full w-full object-contain"
        />
        <div class="absolute left-8 top-8 z-10">
          <MBWLogo class="h-16 w-auto drop-shadow-lg transition-all duration-300 hover:drop-shadow-xl" />
        </div>
      </div>
    </div>
    <!-- Nửa phải: Chọn mẫu website -->
    <div class="relative col-span-1 flex flex-col h-full w-full items-center justify-center bg-white overflow-hidden">
      <div class="w-full max-w-4xl mx-auto p-8">
        <h2 class="text-xl font-bold mb-2">Chọn mẫu website</h2>
        <p class="text-gray-600 mb-6">Dưới đây là các mẫu website.</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 mb-8">
          <div
            v-for="(template, idx) in templates"
            :key="template.key"
            class="bg-white border rounded-xl shadow hover:shadow-lg transition-all flex flex-col items-center p-4"
            :class="{'ring-2 ring-blue-400': selectedTemplate === template.key}"
          >
            <img :src="template.img" alt="" class="w-full h-24 object-contain mb-3 rounded" />
            <div class="font-semibold text-base mb-2 text-center">{{ template.name }}</div>
            <div class="flex gap-2 mt-auto">
              <button class="border border-red-600 text-red-600 px-3 py-1 rounded hover:bg-red-50 text-sm" @click="previewTemplate(template)">Xem thử</button>
              <button class="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-sm" @click="selectTemplate(template.key)">Chọn</button>
            </div>
          </div>
        </div>
        <div class="flex justify-end">
          <button
            class="bg-red-600 text-white px-5 py-2 rounded hover:bg-red-700 transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !selectedTemplate }"
            :disabled="!selectedTemplate"
            @click="goNext"
          >
            Tiếp theo
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Preview -->
    <div v-if="previewingTemplate" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-5xl relative flex flex-col" style="max-height: 90vh;">
        <div class="flex items-center justify-between p-4 border-b">
          <span class="font-semibold">Xem trước mẫu: {{ previewingTemplate.name }}</span>
          <div class="flex items-center gap-2">
            <button :class="{'bg-gray-200': previewMode==='desktop'}" class="p-2 rounded" @click="switchPreviewMode('desktop')" title="Desktop">🖥️</button>
            <button :class="{'bg-gray-200': previewMode==='mobile'}" class="p-2 rounded" @click="switchPreviewMode('mobile')" title="Mobile">📱</button>
            <button class="ml-2 text-gray-500 hover:text-red-500" @click="closePreview" title="Đóng">✖️</button>
          </div>
        </div>
        <div class="flex-1 overflow-auto flex justify-center items-center bg-gray-50 p-4">
          <iframe
            :src="`/template/${previewingTemplate.key}.html`"
            :style="previewMode==='desktop' 
              ? 'width: 1200px; height: 700px; border:1px solid #eee; background:white;' 
              : 'width: 375px; height: 700px; border:1px solid #eee; background:white;'"
            class="rounded shadow"
          ></iframe>
        </div>
        <div class="flex justify-end p-4 border-t">
          <button class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700" @click="choosePreviewedTemplate">
            Chọn mẫu này
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'TemplateSelector',
  props: ['productId'],
  components: {
    // MBWLogo
  },
  data() {
    return {
      selectedTemplate: null,
      previewingTemplate: null,
      previewMode: 'desktop',
      templates: [
        { key: 'modern', name: 'Modern Business', img: '/public/1.png',template_name: 'WT-17235991837942781' },
        { key: 'corporate', name: 'Corporate Plus', img: '/public/2.png', template_name: 'WT-2' },
        { key: 'startup', name: 'Startup', img: '/public/3.png', template_name: 'WT-3' },
        { key: 'portfolio', name: 'Portfolio Pro', img: '/public/4.png', template_name: 'WT-4' },
        { key: 'recruitment', name: 'Recruitment Pro', img: '/public/5.png', template_name: 'WT-5' },
        { key: 'landing', name: 'Landing Pro', img: '/public/6.png', template_name: 'WT-6' },
        { key: 'ecommerce', name: 'E-commerce Plus', img: '/public/7.png', template_name: 'WT-7' },
        { key: 'service', name: 'Service Pro', img: '/public/8.png', template_name: 'WT-8' },
      ],
    };
  },
  computed: {
    saasProduct() {
      return this.$resources.saasProduct?.doc;
    },
  },
  methods: {
    previewTemplate(template) {
      this.previewingTemplate = template;
      this.previewMode = 'desktop';
    },
    closePreview() {
      this.previewingTemplate = null;
    },
    switchPreviewMode(mode) {
      this.previewMode = mode;
    },
    choosePreviewedTemplate() {
      this.selectedTemplate = this.previewingTemplate.key;
      this.closePreview();
    },
    selectTemplate(key) {
      this.selectedTemplate = key;
    },
    goNext() {
      if (this.selectedTemplate && this.saasProduct && this.saasProduct.name) {
        // Tìm template đang được chọn
        const selected = this.templates.find(t => t.key === this.selectedTemplate);
        // Nếu có trường template_name thì lấy template_name, không thì lấy key
        const templateValue = selected?.template_name || this.selectedTemplate;
        this.$router.push({
          path: `/create-site/${this.saasProduct.name}/plan`,
          query: {
            selected_template: templateValue
          }
        });
      }
    },
  },
  resources: {
    saasProduct() {
      return {
        type: 'document',
        doctype: 'Product Trial',
        name: this.productId,
        auto: true,
      };
    },
  },
};
</script> 