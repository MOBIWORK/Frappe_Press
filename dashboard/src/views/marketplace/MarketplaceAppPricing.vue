<script setup>
import { ref, reactive } from 'vue';
import { createResource } from 'frappe-ui';
import AppPlanCard from '@/components/AppPlanCard.vue';
import PrinterIcon from '@/components/PrinterIcon.vue';
import { translate } from '@/utils/index';

const showEditPlanDialog = ref(false);
const currentEditingPlan = reactive({
	price_inr: 0,
	price_usd: 0,
	price_vnd: 0,
	features: [''],
	plan_title: '',
	enabled: true
});

const props = defineProps({
	app: Object
});

const appPlans = createResource({
	url: 'press.api.marketplace.get_app_plans',
	params: {
		app: props.app?.name,
		include_disabled: true
	},
	auto: true
});

const updateAppPlan = createResource({
	url: 'press.api.marketplace.update_app_plan',
	onSuccess() {
		refreshState();
	}
});

const createAppPlan = createResource({
	url: 'press.api.marketplace.create_app_plan',
	validate() {
		if (!currentEditingPlan.plan_title) {
			return translate('Plan_name_is_required');
		}
	},
	onSuccess() {
		refreshState();
	}
});

function editPlan(plan) {
	refreshState();
	if (plan) {
		Object.assign(currentEditingPlan, plan);
		currentEditingPlan.enabled = Boolean(plan.enabled);
		currentEditingPlan.price_vnd = plan.price_vnd;
		currentEditingPlan.features = Array.from(plan.features); // Non-reference copy
	}
	showEditPlanDialog.value = true;
}

function addFeatureInput() {
	currentEditingPlan.features.push('');
}

function deleteFeatureInput(idx) {
	currentEditingPlan.features.splice(idx, 1);
}

function savePlan() {
	if (currentEditingPlan.name) {
		updateAppPlan.submit({
			app_plan_name: currentEditingPlan.name,
			updated_plan_data: currentEditingPlan,
			lang: 'vi'
		});
	} else {
		createAppPlan.submit({
			plan_data: currentEditingPlan,
			marketplace_app: props.app?.name,
			lang: 'vi'
		});
	}
}

function refreshState() {
	appPlans.fetch();
	showEditPlanDialog.value = false;
	resetCurrentEditingPlan();
}

function resetCurrentEditingPlan() {
	Object.assign(currentEditingPlan, {
		price_inr: 0,
		price_usd: 0,
		price_vnd: 0,
		features: [''],
		plan_title: '',
		enabled: true
	});

	updateAppPlan.error = null;
	createAppPlan.error = null;
}
</script>

<template>
	<div>
		<Card
			:title="$t('Pricing_Plans')"
			:subtitle="$t('MarketplaceAppPricing_content_1')"
		>
			<div class="m-4">
				<div class="flex justify-center" v-if="appPlans.loading">
					<Button :loading="true">{{ $t('Loading') }}</Button>
				</div>

				<div v-else-if="appPlans.data">
					<div
						v-if="appPlans.data.length > 0"
						class="mx-auto grid grid-cols-1 gap-2 md:grid-cols-3"
					>
						<AppPlanCard
							v-for="plan in appPlans.data"
							:plan="plan"
							:key="plan.name"
							:clickable="false"
							:editable="true"
							@beginEdit="editPlan(plan)"
						/>
					</div>
					<div v-else>
						<div class="mt-7 flex flex-col items-center justify-center">
							<PrinterIcon class="mb-5 h-20 w-20" />
							<p class="mb-1 text-2xl font-semibold text-gray-900">
								{{ $t('Create_a_plan') }}
							</p>
							<p class="mb-3.5 text-base text-gray-700">
								{{ $t('MarketplaceAppPricing_content_2') }}
							</p>
							<Button variant="solid" @click="editPlan()">{{
								$t('Create_plan')
							}}</Button>
						</div>
					</div>
				</div>
			</div>

			<template v-if="appPlans.data && 0 < appPlans.data.length" #actions>
				<Button @click="editPlan()">{{ $t('New_Plan') }}</Button>
			</template>
		</Card>

		<Dialog :options="{ title: $t('Edit_Plan') }" v-model="showEditPlanDialog">
			<template v-slot:body-content>
				<div>
					<div class="mb-4">
						<input
							type="checkbox"
							id="enabled-checkbox"
							class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							v-model="currentEditingPlan.enabled"
						/>
						<label for="enabled-checkbox" class="ml-1 text-sm text-gray-900">
							{{ $t('Enabled') }}
						</label>
					</div>
					<div class="mb-4">
						<FormControl
							:placeholder="$t('Enter_plan_name')"
							:label="$t('Name')"
							v-model="currentEditingPlan.plan_title"
						></FormControl>
					</div>
					<div class="mb-8">
						<h3 class="mb-4 text-lg font-semibold">
							{{ $t('Subscription_Price') }}
						</h3>
						<div class="grid grid-cols-2 gap-2">
							<FormControl
								:label="`${$t('Price')} VND`"
								v-model="currentEditingPlan.price_vnd"
							></FormControl>
							<!-- <FormControl
								label="Giá INR"
								v-model="currentEditingPlan.price_inr"
							></FormControl>
							<FormControl
								label="Giá USD"
								v-model="currentEditingPlan.price_usd"
							></FormControl> -->
						</div>
					</div>
					<div>
						<h3 class="mb-4 text-lg font-semibold">{{ $t('Features') }}</h3>
						<div>
							<div
								v-for="(feature, idx) in currentEditingPlan.features"
								class="mb-3.5 flex w-full items-stretch"
							>
								<div
									class="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-xs"
								>
									{{ idx + 1 }}
								</div>

								<div class="w-full">
									<FormControl
										class="w-full"
										v-model="currentEditingPlan.features[idx]"
									></FormControl>
								</div>

								<Button
									v-if="idx > 0"
									class="ml-3 rounded-full"
									icon="x"
									@click="deleteFeatureInput(idx)"
								></Button>
							</div>
						</div>
						<div>
							<Button icon-left="plus" @click="addFeatureInput">{{
								$t('Add')
							}}</Button>
						</div>

						<div>
							<ErrorMessage class="mt-3" :message="updateAppPlan.error" />
							<ErrorMessage class="mt-3" :message="createAppPlan.error" />
						</div>
					</div>
				</div>
			</template>

			<template #actions>
				<Button
					class="w-full"
					variant="solid"
					:loading="updateAppPlan.loading || createAppPlan.loading"
					@click="savePlan"
					@close="resetCurrentEditingPlan"
					>{{ $t('Save') }}</Button
				>
			</template>
		</Dialog>
	</div>
</template>
