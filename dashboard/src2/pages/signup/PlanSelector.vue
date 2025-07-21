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
        <div class="relative col-span-1 flex h-full w-full items-center justify-center md:bg-white overflow-hidden">
            <LoginBox :title="__('Select Plan')"
                class="w-full h-full md:h-auto transition-all m-2 lg:m-5 xl:m-8 duration-300 shadow-xl rounded-xl max-w-full"
                customWidth="w-full max-w-none lg:max-w-[95%] xl:max-w-[90%] 2xl:max-w-[85%]">
                <template v-slot:logo v-if="saasProduct">
                    <div class="flex mb-4 w-full justify-center">
                        <img class="h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
                            :src="saasProduct?.logo" alt="Product Logo" />
                    </div>
                </template>

                <!-- Plans in 3 equal columns - Always 3 columns on medium+ screens -->
                <div class="mt-6 w-full overflow-hidden">
                    <div v-if="plans && plans.length"
                        class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-3 lg:gap-4 xl:gap-6 2xl:gap-8 max-h-[60vh] md:max-h-none overflow-y-auto md:overflow-visible">
                        <!-- Custom plan cards with responsive text sizing -->
                        <div v-for="(planItem, index) in plans" :key="index"
                            class="border rounded-lg p-3 md:p-4 lg:p-5 xl:p-6 2xl:p-8 transition-all duration-300 hover:shadow-lg hover:border-red-500 flex flex-col min-h-[300px] md:min-h-[350px] xl:min-h-[400px] 2xl:min-h-[450px] min-w-0 flex-shrink-0"
                            :class="{ 'border-red-500 ring-2 ring-red-200': plan && plan.name === planItem.name }"
                            @click="plan = planItem">
                            <div class="flex-grow overflow-hidden">
                                <div class="mb-3 lg:mb-4 xl:mb-5 border-b border-gray-100 pb-3 lg:pb-4 xl:pb-5">
                                    <div class="flex items-start justify-between mb-2 lg:mb-3">
                                        <h3
                                            class="text-lg sm:text-xl md:text-base lg:text-lg xl:text-xl 2xl:text-2xl font-bold text-gray-900 leading-tight line-clamp-2 break-words">
                                            {{ currentLang === 'vi' ? planItem.title : planItem.title_en }}
                                        </h3>
                                        <span v-if="planItem.popular"
                                            class="ml-2 px-2 py-1 lg:px-3 lg:py-1.5 xl:px-4 xl:py-2 text-xs lg:text-sm font-medium text-white bg-gradient-to-r from-orange-400 to-pink-500 rounded-full flex-shrink-0">
                                            HOT
                                        </span>
                                    </div>
                                    <div
                                        class="flex items-center justify-center w-full px-3 py-1.5 lg:px-6 lg:py-3 xl:px-5 xl:py-2.5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg mb-2">
                                        <span
                                            class="text-base sm:text-lg md:text-sm lg:text-base xl:text-sm 2xl:text-xl font-bold text-blue-700 text-center">
                                            {{ planItem.label }}
                                        </span>
                                    </div>
                                    <p
                                        class="text-xs sm:text-sm md:text-xs lg:text-sm xl:text-base text-gray-600 leading-relaxed">
                                        {{ planItem.sublabel }}
                                    </p>
                                </div>
                                <ul class="my-2 lg:my-3 xl:my-4 space-y-1 lg:space-y-2 xl:space-y-3">
                                    <li v-for="feature in planItem.features" :key="feature.value"
                                        class="flex items-start">
                                        <svg v-if="feature.icon === 'check-circle'" xmlns="http://www.w3.org/2000/svg"
                                            class="h-4 w-4 sm:h-5 sm:w-5 md:h-3 md:w-3 lg:h-4 lg:w-4 xl:h-5 xl:w-5 2xl:h-6 2xl:w-6 mt-0.5 mr-1 lg:mr-2 xl:mr-3 text-green-500 flex-shrink-0"
                                            viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd"
                                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span
                                            class="text-sm sm:text-base md:text-xs lg:text-sm xl:text-base 2xl:text-lg leading-tight break-words min-w-0 flex-1">{{
                                                __(feature.value) }}</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="mt-auto pt-2 lg:pt-3 xl:pt-4 text-center flex-shrink-0">
                                <button
                                    class="rounded-md bg-red-600 px-2 md:px-3 lg:px-4 xl:px-6 2xl:px-8 py-1.5 md:py-2 lg:py-2.5 xl:py-3 2xl:py-4 text-sm sm:text-base md:text-xs lg:text-sm xl:text-base 2xl:text-lg font-medium text-white transform transition-all duration-300 hover:bg-red-700 hover:-translate-y-0.5 w-full"
                                    @click.stop="register(planItem)">
                                    {{ __('Register') }}
                                </button>
                            </div>
                        </div>
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
            return this.$resources.saasProduct?.doc;
        },
        options() {
            console.log("options", this.$resources.options.data);

            return this.$resources.options.data;
        },
        plans() {
            const appSourceDetails = this.options?.app_source_details || [];

            console.log("appSourceDetails", appSourceDetails);

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
            if (this.productId === 'go1_cms') {
                return this.$route.query.selected_template;
            }
            return null;
        }
    },

    methods: {
        register(plan) {
            console.log('Đăng ký gói:', plan);
            // Xử lý logic đăng ký ở đây
            let path = '/';
            if (this.saasProduct) {
                path = `/create-site/${this.saasProduct.name}/policy`;
            }

            const encodedPlan = encodeURIComponent(JSON.stringify(plan));
            const query = { selected_plan: encodedPlan };
            if (this.productId === 'go1_cms' && this.selectedTemplate) {
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
