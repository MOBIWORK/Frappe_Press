<template>
    <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        <!-- Left Column: Background and Logo -->
        <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
            <div v-if="saasProduct"
                class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img :src="saasProduct?.background" alt="Background"
                    class="absolute inset-0 h-full w-full object-contain" />
                <!-- Logo on top -->
            </div>

            <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img src="/public/bg1.png" alt="Background" class="absolute inset-0 h-full w-full object-contain" />
                <!-- Logo on top -->
                <div class="absolute left-8 top-8 z-10">
                    <MBWLogo class="h-16 w-auto drop-shadow-lg transition-all duration-300 hover:drop-shadow-xl" />
                </div>
            </div>
        </div>

        <!-- Right Column: Policy Form -->
        <div
            class="relative col-span-1 flex h-full w-full items-center justify-center py-3 px-3 md:py-6 md:px-6 lg:overflow-auto lg:bg-white overflow-hidden">
            <LoginBox :title="__('Privacy Policy and Services')"
                class="w-full h-full lg:h-auto transition-all m-2 lg:m-5 xl:m-8 duration-300 shadow-xl rounded-xl max-w-full"
                customWidth="w-full max-w-none lg:max-w-[95%] xl:max-w-[90%] 2xl:max-w-[85%]">
                <template v-slot:logo v-if="saasProduct">
                    <div class="flex mb-4 w-full justify-center">
                        <img class="h-12 md:h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
                            :src="saasProduct?.logo" alt="Product Logo" />
                    </div>
                </template>

                <div class="w-full">
                    <div class="w-full border rounded-md p-3 md:p-4 lg:p-5 xl:p-6 text-sm md:text-base">
                        <div
                            class="h-32 md:h-40 lg:h-48 xl:h-56 overflow-y-auto border rounded p-2 md:p-3 lg:p-4 text-justify text-xs md:text-sm lg:text-base bg-white quill-content">
                            <!-- Loading state -->
                            <div v-if="$resources.saasProduct.loading" class="flex items-center justify-center h-full">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                <span class="ml-2 text-gray-600">{{ __('Loading policy...') }}</span>
                            </div>
                            
                            <!-- Display policy content based on current language -->
                            <div v-else-if="currentPolicyContent" v-html="currentPolicyContent" class="ql-editor"></div>
                            
                            <!-- Fallback content when no policy data available -->
                            <div v-else class="text-gray-700 leading-relaxed">
                                <div v-if="currentLang === 'en'" class="space-y-3">
                                    <p><strong>1. Data Collection:</strong> We collect information you provide directly to us when using our services.</p>
                                    <p><strong>2. Data Usage:</strong> We use your information to provide, maintain, and improve our services.</p>
                                    <p><strong>3. Data Protection:</strong> We implement appropriate security measures to protect your personal information.</p>
                                    <p><strong>4. Terms of Use:</strong> By using this application, you agree to our terms of service and privacy policy.</p>
                                    <p><strong>5. Contact:</strong> Please contact us if you have any questions about these terms.</p>
                                    <p class="text-sm text-gray-600 mt-4">This application is provided "as is" without warranty of any kind. We reserve the right to modify these terms at any time.</p>
                                </div>
                                
                                <div v-else class="space-y-3">
                                    <p><strong>1. Thu thập dữ liệu:</strong> Chúng tôi thu thập thông tin mà bạn cung cấp trực tiếp khi sử dụng dịch vụ của chúng tôi.</p>
                                    <p><strong>2. Sử dụng dữ liệu:</strong> Chúng tôi sử dụng thông tin của bạn để cung cấp, duy trì và cải thiện dịch vụ.</p>
                                    <p><strong>3. Bảo vệ dữ liệu:</strong> Chúng tôi thực hiện các biện pháp bảo mật thích hợp để bảo vệ thông tin cá nhân của bạn.</p>
                                    <p><strong>4. Điều khoản sử dụng:</strong> Bằng việc sử dụng ứng dụng này, bạn đồng ý với các điều khoản dịch vụ và chính sách bảo mật của chúng tôi.</p>
                                    <p><strong>5. Liên hệ:</strong> Vui lòng liên hệ với chúng tôi nếu bạn có bất kỳ câu hỏi nào về các điều khoản này.</p>
                                    <p class="text-sm text-gray-600 mt-4">Ứng dụng này được cung cấp "như là" mà không có bảo đảm gì. Chúng tôi có quyền sửa đổi các điều khoản này bất cứ lúc nào.</p>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-center mt-3 lg:mt-4">
                            <Checkbox size="sm" :value="false" v-model="checkPolicy"
                                :label="__('I have read and agree to the above terms')"
                                class="text-xs md:text-sm lg:text-base" />
                        </div>

                        <button :disabled="!checkPolicy || isLoading" @click="handleSubmit" :class="[
                            'w-full mt-3 lg:mt-4 py-2 md:py-2.5 lg:py-3 rounded text-sm md:text-base lg:text-lg font-semibold transition-colors duration-200',
                            checkPolicy && !isLoading
                                ? 'bg-red-600 hover:bg-red-700 text-white cursor-pointer transform hover:-translate-y-0.5'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        ]">
                            <span v-if="isLoading" class="flex items-center justify-center">
                                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                {{ __('Loading...') }}
                            </span>
                            <span v-else>{{ __('Confirm') }}</span>
                        </button>
                    </div>
                </div>

                <!-- Language Selector -->
                <template v-slot:footer>
                    <div class="flex items-center justify-center py-4 border-t border-gray-100 mt-6 w-full">
                        <SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
                    </div>
                </template>
            </LoginBox>
        </div>
    </div>
</template>

<script>
import LoginBox from '../../components/auth/LoginBox.vue';
import SelectLanguage from '../../components/SelectLanguage.vue';
import { Checkbox } from 'frappe-ui';

export default {
    name: "SignupPolicy",
    props: ['productId'],
    components: {
        LoginBox,
        SelectLanguage,
        Checkbox
    },

    data() {
        return {
            checkPolicy: false,
            currentLang: localStorage.getItem('lang') || 'vi'
        };
    },
    
    mounted() {
        window.addEventListener('storage', this.handleStorageChange);
        window.addEventListener('languageChanged', this.handleLanguageChange);
    },
    
    beforeUnmount() {
        window.removeEventListener('storage', this.handleStorageChange);
        window.removeEventListener('languageChanged', this.handleLanguageChange);
    },
    
    methods: {
        handleStorageChange(e) {
            if (e.key === 'lang') {
                this.currentLang = e.newValue || 'vi';
            }
        },
        
        handleLanguageChange() {
            this.currentLang = localStorage.getItem('lang') || 'vi';
        },
        
        async handleSubmit() {
            if (!this.checkPolicy) return;
            if (!this.saasProduct) return;
            // Gọi API kiểm tra user/site/app
            const res = await this.$resources.mySiteInfo.fetch();
            const data = res && res.data ? res.data : res;
            let path = '/';
            const productId = this.saasProduct.name;
            // Nếu đã có site và chưa có app (productId) trong list_app
            if (data.site && !(data.list_app && data.list_app.includes(productId))) {
                path = `/create-site/${productId}/install-app-setup`;
            } else {
                // Nếu chưa có site hoặc đã có app thì vẫn đi flow cũ
                path = `/create-site/${productId}/setup`;
            }
            const encodedPlan = encodeURIComponent(JSON.stringify(this.selectedPlan));
            const query = { selected_plan: encodedPlan };
            if (this.productId === 'go1_cms' && this.selectedTemplate) {
                query.selected_template = this.selectedTemplate;
            }
            
            // Add language preference to query parameters
            const currentLang = localStorage.getItem('lang') || 'vi';
            if (currentLang) {
                query.lang = currentLang;
            }
            
            this.$router.push({ path, query });
        }
    },
    
    resources: {
        saasProduct() {
            return {
                url: 'press.api.product_trial.get_product_trial_details',
                params: {
                    product_id: this.productId
                },
                auto: true,
                cache: false, // Disable cache to always fetch fresh data

            };
        },
        mySiteInfo() {
            return {
                url: 'press.api.site.is_check_user',
                params: {
                    email: localStorage.getItem('login_email'),
                },
                auto: true,
            };
        },

    },

    computed: {
        saasProduct() {
            return this.$resources.saasProduct?.data;
        },
        currentPolicyContent() {
            if (!this.saasProduct) return null;

            if (this.currentLang === 'en') {
                return this.saasProduct.policy_app_en || this.saasProduct.policy_app_vn;
            } else {
                return this.saasProduct.policy_app_vn || this.saasProduct.policy_app_en;
            }
        },
        hasPolicy() {
            return this.currentPolicyContent || !this.$resources.saasProduct.loading;
        },
        isLoading() {
            return this.$resources.saasProduct.loading;
        },
        selectedPlan() {
            try {
                const raw = this.$route.query.selected_plan;
                if (raw) {
                    const decoded = decodeURIComponent(raw);
                    return JSON.parse(decoded);
                }
            } catch (error) {
                console.error("Error parsing selected plan:", error);
            }
            return null;
        },
        selectedTemplate() {
            if (this.productId === 'go1_cms') {
                return this.$route.query.selected_template;
            }
            return null;
        }
    },
}
</script>

<style scoped>
/* Quill Editor Styling */
.quill-content .ql-editor {
    padding: 0;
    border: none;
    font-family: inherit;
    line-height: 1.6;
    color: #374151;
}

.quill-content .ql-editor p {
    margin-bottom: 1rem;
    line-height: 1.6;
}

.quill-content .ql-editor p:last-child {
    margin-bottom: 0;
}

.quill-content .ql-editor strong {
    font-weight: 600;
    color: #1f2937;
}

.quill-content .ql-editor ol {
    margin: 1rem 0;
    padding-left: 0;
    list-style: none;
    counter-reset: list-counter;
}

.quill-content .ql-editor ol li {
    margin-bottom: 0.75rem;
    padding-left: 1.5rem;
    position: relative;
    line-height: 1.6;
    counter-increment: list-counter;
}

.quill-content .ql-editor ol li:before {
    content: counter(list-counter) ".";
    position: absolute;
    left: 0;
    top: 0;
    color: #4f46e5;
    font-weight: 600;
}

.quill-content .ql-editor ol li[data-list="bullet"] {
    counter-increment: none;
}

.quill-content .ql-editor ol li[data-list="bullet"]:before {
    content: "•";
    color: #4f46e5;
    font-size: 1.2em;
    line-height: 1;
}

.quill-content .ql-editor .ql-ui {
    display: none;
}

.quill-content .ql-editor h1,
.quill-content .ql-editor h2,
.quill-content .ql-editor h3,
.quill-content .ql-editor h4,
.quill-content .ql-editor h5,
.quill-content .ql-editor h6 {
    font-weight: 600;
    color: #1f2937;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

.quill-content .ql-editor h1 { font-size: 1.5rem; }
.quill-content .ql-editor h2 { font-size: 1.375rem; }
.quill-content .ql-editor h3 { font-size: 1.25rem; }
.quill-content .ql-editor h4 { font-size: 1.125rem; }
.quill-content .ql-editor h5 { font-size: 1rem; }
.quill-content .ql-editor h6 { font-size: 0.875rem; }

.quill-content .ql-editor ul {
    margin: 1rem 0;
    padding-left: 1.5rem;
}

.quill-content .ql-editor ul li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
}

.quill-content .ql-editor blockquote {
    border-left: 4px solid #e5e7eb;
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: #6b7280;
}

.quill-content .ql-editor code {
    background-color: #f3f4f6;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.875em;
}

.quill-content .ql-editor pre {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
}

.quill-content .ql-editor a {
    color: #3b82f6;
    text-decoration: underline;
}

.quill-content .ql-editor a:hover {
    color: #1d4ed8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .quill-content .ql-editor {
        font-size: 0.875rem;
    }
    
    .quill-content .ql-editor h1 { font-size: 1.25rem; }
    .quill-content .ql-editor h2 { font-size: 1.125rem; }
    .quill-content .ql-editor h3 { font-size: 1rem; }
    .quill-content .ql-editor h4 { font-size: 0.875rem; }
}

@media (min-width: 1024px) {
    .quill-content .ql-editor {
        font-size: 1rem;
    }
}
</style>