<template>
    <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        <!-- Left Column: Background and Logo -->
        <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
            <div v-if="saasProduct"
                class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img :src="saasProduct?.background" alt="Background"
                    class="absolute inset-0 h-full w-full object-contain" />
            </div>

            <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img src="/public/bg1.png" alt="Background" class="inset-0 h-full w-full object-contain" />
            </div>
        </div>

        <!-- Right Column: Plan Selection Form -->
        <div class="relative col-span-1 flex h-full w-full items-center justify-center py-2 px-2 sm:py-3 sm:px-3 md:py-6 md:px-6 lg:overflow-auto lg:bg-white overflow-hidden">
            <LoginBox :title="__('Select Plan')"
                class="w-full h-full lg:h-auto transition-all m-1 sm:m-2 lg:m-5 xl:m-8 duration-300 shadow-xl rounded-xl max-w-full"
                customWidth="w-full max-w-none lg:max-w-[95%] xl:max-w-[90%] 2xl:max-w-[85%]">
                <template v-slot:logo v-if="saasProduct">
                    <div class="flex mb-2 sm:mb-3 md:mb-4 w-full justify-center">
                        <img class="h-10 sm:h-12 md:h-14 lg:h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
                            :src="saasProduct?.logo" alt="Product Logo" />
                    </div>
                </template>

                <!-- Plans in responsive grid -->
                <div class="mt-3 sm:mt-4 md:mt-6 w-full overflow-hidden">
                    <div v-if="plans && plans.length"
                        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3 md:gap-4 lg:gap-3 xl:gap-4 2xl:gap-6 max-h-[70vh] sm:max-h-[75vh] md:max-h-[80vh] lg:max-h-none overflow-y-auto lg:overflow-visible">
                        <!-- Custom plan cards with enhanced responsive design -->
                        <div v-for="(planItem, index) in plans" :key="index"
                            class="border rounded-lg p-2 sm:p-3 md:p-4 lg:p-4 xl:p-5 2xl:p-6 transition-all duration-300 hover:shadow-lg hover:border-red-500 flex flex-col min-h-[280px] sm:min-h-[320px] md:min-h-[350px] lg:min-h-[380px] xl:min-h-[400px] 2xl:min-h-[420px] min-w-0 flex-shrink-0"
                            :class="{ 'border-red-500 ring-2 ring-red-200': plan && plan.name === planItem.name }"
                            @click="plan = planItem">
                            <div class="flex-grow overflow-hidden">
                                <div class="mb-2 sm:mb-3 lg:mb-4 border-b border-gray-100 pb-2 sm:pb-3 lg:pb-4">
                                    <div class="flex items-start justify-between mb-1 sm:mb-2">
                                        <h3
                                            class="text-sm sm:text-base md:text-lg lg:text-base xl:text-lg 2xl:text-xl font-bold text-gray-900 leading-tight line-clamp-2 break-words">
                                            {{ currentLang === 'vi' ? planItem.title : planItem.title_en }}
                                        </h3>
                                        <span v-if="planItem.popular"
                                            class="ml-1 sm:ml-2 px-1.5 sm:px-2 lg:px-3 py-0.5 sm:py-1 lg:py-1.5 text-xs lg:text-sm font-medium text-white bg-gradient-to-r from-orange-400 to-pink-500 rounded-full flex-shrink-0">
                                            HOT
                                        </span>
                                    </div>
                                    <div
                                        class="flex items-center justify-center w-full px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg mb-1 sm:mb-2">
                                        <span
                                            class="text-sm sm:text-base md:text-lg lg:text-sm xl:text-base 2xl:text-lg font-bold text-blue-700 text-center">
                                            {{ planItem.label }}
                                        </span>
                                    </div>
                                    <p
                                        class="text-xs sm:text-sm md:text-base lg:text-sm xl:text-base text-gray-600 leading-relaxed">
                                        {{ planItem.sublabel }}
                                    </p>
                                </div>
                                <ul class="my-1 sm:my-2 lg:my-3 space-y-1 sm:space-y-1.5 lg:space-y-2">
                                    <li v-for="feature in planItem.features" :key="feature.value"
                                        class="flex items-start">
                                        <svg v-if="feature.icon === 'check-circle'" xmlns="http://www.w3.org/2000/svg"
                                            class="h-3 w-3 sm:h-4 sm:w-4 md:h-5 md:w-5 lg:h-4 lg:w-4 xl:h-5 xl:w-5 mt-0.5 mr-1 sm:mr-2 text-green-500 flex-shrink-0"
                                            viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd"
                                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span
                                            class="text-xs sm:text-sm md:text-base lg:text-sm xl:text-base leading-tight break-words min-w-0 flex-1">{{
                                                __(feature.value) }}</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="mt-auto pt-2 sm:pt-3 lg:pt-4 text-center flex-shrink-0">
                                <button
                                    class="rounded-md bg-red-600 px-2 sm:px-3 md:px-4 lg:px-3 xl:px-4 2xl:px-6 py-1 sm:py-1.5 md:py-2 lg:py-2 xl:py-2.5 2xl:py-3 text-xs sm:text-sm md:text-base lg:text-sm xl:text-base 2xl:text-lg font-medium text-white transform transition-all duration-300 hover:bg-red-700 hover:-translate-y-0.5 w-full"
                                    @click.stop="register(planItem)">
                                    {{ __('Register') }}
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Loading state -->
                    <div v-else-if="$resources.options.loading" class="flex items-center justify-center py-8 sm:py-12 md:py-16">
                        <div class="animate-spin rounded-full h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 border-b-2 border-red-600"></div>
                        <span class="ml-2 sm:ml-3 text-sm sm:text-base text-gray-600">{{ __('Loading plans...') }}</span>
                    </div>
                    
                    <!-- No plans available -->
                    <div v-else class="text-center py-8 sm:py-12 md:py-16">
                        <p class="text-sm sm:text-base md:text-lg text-gray-600">{{ __('No plans available') }}</p>
                    </div>
                </div>

                <!-- Language Selector -->
                <template v-slot:footer>
                    <div class="flex items-center justify-center py-2 sm:py-3 md:py-4 border-t border-gray-100 mt-3 sm:mt-4 md:mt-6 w-full">
                        <SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
                    </div>
                </template>
            </LoginBox>
        </div>
    </div>
</template>
<script>
import { getCachedDocumentResource } from 'frappe-ui';
import LoginBox from '../../components/auth/LoginBox.vue';
import SelectLanguage from '../../components/SelectLanguage.vue';
import PlansCards from '../../components/PlansCards.vue';

export default {
    name: "SignupPlanSelector",
    props: ['productId'],
    components: {
        LoginBox,
        SelectLanguage,
        PlansCards
    },

    data() {
        return {
            plan: null,
            currentLang: localStorage.getItem('lang') || 'vi'
        };
    },
    computed: {
        $site() {
            return getCachedDocumentResource('Site', this.site);
        },
        saasProduct() {
            return this.$resources.saasProduct?.doc
        },
        options() {
            return this.$resources.options.data;
        },
        plans() {
            const appSourceDetails = this.options?.app_source_details || [];

            // Tìm object có app trùng với productId
            const matchedApp = appSourceDetails.find(app => app.app === this.productId);
            if (!matchedApp) return [];

            const planData = matchedApp.plans || [];
            return planData.map(plan => ({
                label: this.getPlanLabel(plan),
                sublabel: ' ',
                ...plan,
                features: (plan.features || []).map(f => ({
                    value: f,
                    icon: 'check-circle'
                }))
            }));
        },
        selectedTemplate() {
            if (this.productId === 'go1_cms' || this.productId === 'mbw_cms') {
                return this.$route.query.selected_template;
            }
            return null;
        }
    },

    methods: {
        register(plan) {
            let path = '/';
            if (this.saasProduct) {
                path = `/create-site/${this.saasProduct.name}/policy`;
            }

            const encodedPlan = encodeURIComponent(JSON.stringify(plan));
            const query = { selected_plan: encodedPlan };
            if ((this.productId === 'go1_cms' || this.productId === 'mbw_cms') && this.selectedTemplate) {
                query.selected_template = this.selectedTemplate;
            }
            this.$router.push({ path, query });
        },
        getPlanLabel(plan) {
            if (plan.price_vnd > 0) {
                // Sử dụng hàm formatVND để định dạng tiền Việt Nam
                return `${this.$format.formatVND(plan.price_vnd)} VNĐ/${__('month')}`;
            } else if (plan.price_inr === 0 || plan.price_usd === 0) {
                return 'Free';
            } else {
                return `${this.$format.userCurrency(
                    this.$team.doc.currency === 'INR'
                        ? plan.price_inr
                        : plan.price_usd
                )}/${__('month')}`;
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
        options() {
            return {
                url: 'press.api.site.options_for_new',
                onSuccess() {
                    if (this.options.versions.length > 0) {
                        this.version = this.options.versions[0].name;
                    }
                },
                auto: true,
            };
        },
    },
};
</script>
