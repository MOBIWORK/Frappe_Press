<template>
    <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        <!-- Left Column: Background and Logo -->
        <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
            <div v-if="saasProduct" class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img 
                    :src="saasProduct?.background" 
                    alt="Background" 
                    class="absolute inset-0 h-full w-full object-contain"
                />
                <!-- Logo on top -->
            </div>

            <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img 
                    src="/public/bg1.png" 
                    alt="Background"
                    class="absolute inset-0 h-full w-full object-contain"
                />
            </div>
        </div>

        <!-- Right Column: Plan Selection Form -->
        <div class="relative col-span-1 flex h-full w-full items-center justify-center md:bg-white overflow-hidden">
            <LoginBox
                class="w-full h-full md:h-auto transition-all m-2 lg:m-5 xl:m-8 duration-300 shadow-xl rounded-xl max-w-full"
                customWidth="w-full max-w-none lg:max-w-[95%] xl:max-w-[90%] 2xl:max-w-[85%]">
                <template v-slot:logo v-if="saasProduct">
                    <div class="flex mb-4 w-full justify-center">
                        <img class="h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
                            :src="saasProduct?.logo" alt="Product Logo" />
                    </div>
                </template>

                <!-- Plans in 3 equal columns - Always 3 columns on medium+ screens -->
                <h2 class="text-lg font-semibold mb-2">{{ __('Infomation current site and registered applications') }}</h2>
                <Summary :options="siteSummaryOptions" />

                <div v-if="siteInfo && siteInfo.site" class="mt-6 text-center">
                    <a :href="`https://${siteInfo.site}`" target="_blank"
                        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        {{ __('Go to site') }}
                    </a>
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
import Summary from '../../components/Summary.vue';

export default {
    name: 'SetupSiteSummary',
    props: ['productId'],
    components: { LoginBox, Summary },
    data() {
        return {

        };
    },
    resources: {
        mySiteInfo() {
            return {
                url: 'press.api.site.is_check_user', // <-- Đổi thành API thực tế của bạn
                params: {
                    email: localStorage.getItem('login_email'),
                },
                auto: true,
            };
        },
        saasProduct() {
            return {
                type: 'document',
                doctype: 'Product Trial',
                name: this.productId,
                auto: true,
            };
        },
    },
    computed: {
        saasProduct() {
            return this.$resources.saasProduct?.doc;
        },
        siteInfo() {
            console.log("this.$resources.mySiteInfo.data", this.$resources.mySiteInfo.data)
            return this.$resources.mySiteInfo.data;
        },
        siteSummaryOptions() {
            if (!this.siteInfo) return [];

            const appDetails = this.siteInfo.app_details || [];
            const appsValue = appDetails
                .map(detail => {
                    if (!detail.plan_info) return null;
                    const lang = localStorage.getItem('lang')
                    const planTitle =
                        lang === 'vi' && detail.plan_info.title
                            ? detail.plan_info.title
                            : detail.plan_info.title_en;

                    const price = (detail.plan_info.price_vnd || 0).toLocaleString('vi-VN', {
                        style: 'currency',
                        currency: 'VND',
                    });

                    return `${detail.app_title} - ${planTitle}`;
                })
                .filter(Boolean)
                .join('<br>');

            const options = [
                {
                    label: __('Site name'),
                    value: this.siteInfo.site,
                },
            ];

            if (appsValue) {
                options.unshift({
                    label: __('Apps'),
                    value: appsValue,
                });
            }

            return options;
        },
    },
    methods: {
    },
};
</script>