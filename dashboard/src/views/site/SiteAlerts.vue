<script setup>
import { computed, ref, defineAsyncComponent } from 'vue';
import { utils } from '@/utils';
import { createResource } from 'frappe-ui';
import AlertSiteUpdate from '@/components/AlertSiteUpdate.vue';
import AlertSiteActivation from '@/components/AlertSiteActivation.vue';
import { translate } from '@/utils/index';

const SitePlansDialog = defineAsyncComponent(() =>
	import('./SitePlansDialog.vue')
);
const BillingInformationDialog = defineAsyncComponent(() =>
	import('@/components/BillingInformationDialog.vue')
);

const props = defineProps({ site: Object, plan: Object });
const showPromotionalDialog = ref(false);
const clickedPromotion = ref(null);
const showBillingDialog = ref(false);
const showChangePlanDialog = ref(false);

const closeToLimits = computed(() => {
	if (!(props.site && props.plan)) return false;
	let usage = props.plan.usage_in_percent;
	return [usage.cpu, usage.database, usage.disk].some(x => 100 >= x && x > 80);
});

const limitExceeded = computed(() => {
	if (!(props.site && props.plan)) return false;
	let usage = props.plan.usage_in_percent;
	return [usage.cpu, usage.database, usage.disk].some(x => x > 100);
});

const isInTrial = computed(() => {
	return props.site?.trial_end_date;
});

const trialEndsText = computed(() => {
	if (!props.site?.trial_end_date) {
		return 0;
	}
	return utils.methods.trialEndsInDaysText(props.site.trial_end_date);
});

const siteMigrationText = computed(() => {
	const status = props.site?.site_migration.status;

	if (status === 'Running') {
		return translate('SiteAlerts_content_1');
	} else if (status === 'Pending') {
		return translate('SiteAlerts_content_2');
	} else if (status === 'Scheduled') {
		return `${translate('SiteAlerts_content_3')} ${utils.methods.formatDate(
			props.site?.site_migration.scheduled_time,
			'relative'
		)}.`;
	}
});

const siteVersionUpgradeText = computed(() => {
	const status = props.site?.version_upgrade.status;

	if (status === 'Running') {
		return translate('SiteAlerts_content_4');
	} else if (status === 'Pending') {
		return translate('SiteAlerts_content_5');
	} else if (status === 'Scheduled') {
		return `${translate('SiteAlerts_content_6')} ${utils.methods.formatDate(
			props.site?.version_upgrade.scheduled_time,
			'relative'
		)}.`;
	}
});

const marketplacePromotionalBanners = createResource({
	url: 'press.api.marketplace.get_promotional_banners',
	auto: true
});
</script>

<template>
	<div class="space-y-2">
		<AlertSiteActivation :site="site" />
		<AlertSiteUpdate :site="site" />

		<div
			v-if="
				marketplacePromotionalBanners.data &&
				marketplacePromotionalBanners.data.length > 0
			"
		>
			<Alert
				v-for="banner in marketplacePromotionalBanners.data"
				:title="banner.alert_title"
				:key="banner.name"
			>
				{{ banner.alert_message }}

				<template #actions>
					<Button
						class="whitespace-nowrap"
						variant="solid"
						@click="
							() => {
								showPromotionalDialog = true;
								clickedPromotion = banner;
							}
						"
					>
						{{ $t('Learn_More') }}
					</Button>
				</template>
			</Alert>
		</div>
		<Alert :title="$t('Trial')" v-if="isInTrial && $account.hasBillingInfo">
			{{ $t('SiteAlerts_content_7') }} {{ trialEndsText
			}}{{ $t('SiteAlerts_content_8') }}

			<template #actions>
				<Button
					class="whitespace-nowrap"
					@click="showBillingDialog = true"
					variant="solid"
				>
					{{ $t('Add_Billing_Information') }}
				</Button>
			</template>
		</Alert>
		<Alert :title="$t('Trial')" v-if="isInTrial && $account.hasBillingInfo">
			{{ $t('SiteAlerts_content_9') }} {{ trialEndsText
			}}{{ $t('SiteAlerts_content_10') }}

			<template #actions>
				<Button
					class="whitespace-nowrap"
					@click="showChangePlanDialog = true"
					variant="solid"
				>
					{{ $t('Select_Plan') }}
				</Button>
			</template>
		</Alert>
		<Alert :title="$t('Attention_Required')" v-if="limitExceeded">
			{{ $t('SiteAlerts_content_11') }}
		</Alert>
		<Alert :title="$t('Attention_Required')" v-else-if="closeToLimits">
			{{ $t('SiteAlerts_content_12') }}
		</Alert>

		<Alert :title="$t('Site_Migration')" v-if="site?.site_migration">
			{{ siteMigrationText }}
			<template #actions>
				<Button
					v-if="
						site.site_migration.status === 'Running' &&
						site.site_migration.job_id
					"
					class="whitespace-nowrap"
					variant="solid"
					:route="{
						name: 'SiteJobs',
						params: { jobName: site.site_migration.job_id }
					}"
				>
					{{ $t('View_Job') }}
				</Button>
			</template>
		</Alert>

		<Alert :title="$t('Version_Upgrade')" v-if="site?.version_upgrade">
			{{ siteVersionUpgradeText }}
			<template #actions>
				<Button
					v-if="
						site.version_upgrade.status === 'Running' &&
						site.version_upgrade.job_id
					"
					class="whitespace-nowrap"
					variant="solid"
					:route="{
						name: 'SiteJobs',
						params: { jobName: site.version_upgrade.job_id }
					}"
				>
					{{ $t('View_Job') }}
				</Button>
			</template>
		</Alert>

		<Dialog
			v-model="showPromotionalDialog"
			@close="e => (clickedPromotion = null)"
			:options="{
				title: 'MBWCloud Marketplace',
				actions: [
					{
						variant: 'solid',
						route: `/install-app/${clickedPromotion?.app}`,
						label: $t('Install_App')
					}
				]
			}"
		>
			<template #body-content>
				<div v-if="clickedPromotion" class="flex flex-row items-center">
					<Avatar
						class="mr-2"
						size="lg"
						shape="square"
						:image="clickedPromotion.image"
						:label="clickedPromotion.title"
					/>

					<div class="flex flex-col">
						<h4 class="text-xl font-semibold text-gray-900">
							{{ clickedPromotion.title }}
						</h4>
						<p class="text-base text-gray-600">
							{{ clickedPromotion.description }}
						</p>
					</div>
				</div>
			</template>
		</Dialog>

		<BillingInformationDialog
			v-model="showBillingDialog"
			v-if="showBillingDialog"
		/>

		<SitePlansDialog
			v-model="showChangePlanDialog"
			:site="site"
			:plan="plan"
			@plan-change="() => $emit('plan-change')"
		/>
	</div>
</template>
