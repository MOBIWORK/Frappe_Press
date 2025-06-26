<template>
    <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        <!-- Left Column: Background and Logo -->
        <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
            <div v-if="saasProduct"
                class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <img :src="saasProduct?.background" alt="Background"
                    class="absolute inset-0 h-full w-full object-contain" />
            </div>
            <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <img src="/public/bg1.png" alt="Background" class="absolute inset-0 h-full w-full object-contain" />
            </div>
        </div>
        <!-- Right Column: Site/App Summary -->
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
                <div class="mb-6">
                    <h2 class="text-lg font-semibold mb-2">{{ __('Infomation current site and registered applications') }}</h2>
                    <Summary :options="existingSummaryOptions" />
                </div>
                <div class="mb-6">
                    <h2 class="text-lg font-semibold mb-2">{{ __('New registration application information') }}</h2>
                    <Summary :options="newPlanSummaryOptions" />
                </div>
                <div class="mt-6 text-center">
                    <div v-if="installSuccess" class="mb-4">
                        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
                            <strong class="font-bold">{{ __('Success') }}! </strong>
                            <span class="block sm:inline">{{ __('App installed successfully.') }}</span>
                        </div>
                    </div>
                    <div v-if="installError" class="mb-4">
                        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                            <strong class="font-bold">{{ __('Error') }}! </strong>
                            <span class="block sm:inline">{{ installError }}</span>
                        </div>
                    </div>
                    <button v-if="!installSuccess && !isAppInstalled" @click="handleInstallApp"
                        :disabled="installLoading"
                        class="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        <svg v-if="installLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                        </svg>
                        {{ installLoading ? __('Installing...') : __('Install app') }}
                    </button>
                </div>
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
import SelectLanguage from '../../components/SelectLanguage.vue';

export default {
    name: 'SetupInstallApp',
    props: ['productId'],
    components: { LoginBox, Summary, SelectLanguage },
    data() {
        return {
            installSuccess: false,
            installError: '',
            installLoading: false,
        };
    },
    resources: {
        mySiteInfo() {
            return {
                url: 'press.api.site.is_check_user',
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
        options() {
            return {
                url: 'press.api.site.options_for_new',
                onSuccess(data) {
                    if (data.versions && data.versions.length > 0) {
                        this.version = data.versions[0].name;
                    }
                },
                auto: true,
            };
        },
        installApp() {
            return {
                url: 'press.api.client.run_doc_method',
                makeParams: () => {
                    return {
                        dt: 'Site',
                        dn: this.siteInfo.site,
                        method: 'install_app',
                        args: {
                            app: this.productId,
                            plan: this.selectedPlan.name
                        }
                    };
                },
                auto: false,
                onSuccess: (data) => {
                    this.installSuccess = true;
                    this.installError = '';
                },
                onError: (err) => {
                    this.installError = (err && err.message) ? err.message : (err && err.toString ? err.toString() : 'Install app failed');
                    this.installSuccess = false;
                }
            };
        },
    },
    computed: {
        saasProduct() {
            return this.$resources.saasProduct?.doc;
        },
        siteInfo() {
            return this.$resources.mySiteInfo.data;
        },
        options() {
            return this.$resources.options.data
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
        existingSummaryOptions() {
            if (!this.siteInfo) return [];
            const appDetails = this.siteInfo.app_details || [];
            const appsValue = appDetails
                .map(detail => {
                    if (!detail.plan_info) return null;
                    const lang = localStorage.getItem('lang');
                    const planTitle =
                        lang === 'vi' && detail.plan_info.title
                            ? detail.plan_info.title
                            : detail.plan_info.title_en;
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
                    label: __('Registered application'),
                    value: appsValue,
                });
            }
            return options;
        },
        newPlanSummaryOptions() {
            if (!this.selectedPlan) return [];
            const appSource = this.options?.app_source_details?.find(
                (app) => app.app === this.productId
            );
            const lang = localStorage.getItem('lang');
            

            return [
                {
                    label: __('Application name'),
                    value: appSource ? appSource.app_title : '',
                },
                {
                    label: __('Plan name'),
                    value: lang === 'vi' && this.selectedPlan.title ? this.selectedPlan.title : this.selectedPlan.title_en,
                },
                {
                    label: __('Price plan'),
                    value: `${this.$format.formatVND(this.selectedPlan.price_vnd)} VNĐ`,
                }
            ];
        },
        isAppInstalled() {
            const listApp = this.siteInfo && this.siteInfo.list_app;
            if (Array.isArray(listApp)) {
                return listApp.includes(this.productId);
            }
            return false;
        },
    },
    methods: {
        async handleInstallApp() {
            this.installLoading = true;
            this.installError = '';
            try {
                await this.$resources.installApp.submit();
            } finally {
                this.installLoading = false;
            }
        }
    }
};
</script>
