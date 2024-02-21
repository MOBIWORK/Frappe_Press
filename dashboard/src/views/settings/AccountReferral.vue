<template>
	<Card
		v-if="referralLink"
		:title="$t('refer_and_earn')"
		:subtitle="$t('accountreferral_content_1')"
	>
		<div class="space-y-4">
			<ClickToCopyField :textContent="referralLink" />
			<h3 class="text-base text-gray-700">
				{{ $t('accountreferral_content_2') }}
				{{ minimumSpentAmount }} {{ $t('accountreferral_content_3') }}
				<strong
					>{{ $t('get') }} {{ creditAmountInTeamCurrency }}
					{{ $t('accountreferral_content_4') }}</strong
				>!
			</h3>
		</div>
	</Card>
</template>
<script>
import ClickToCopyField from '@/components/ClickToCopyField.vue';

export default {
	name: 'AccountRefferal',
	components: {
		ClickToCopyField
	},
	computed: {
		referralLink() {
			if (this.$account.team.referrer_id) {
				return `${location.origin}/dashboard/signup?referrer=${this.$account.team.referrer_id}`;
			}
			return '';
		},
		minimumSpentAmount() {
			return (
				this.$formatMoney(this.$account.feature_flags.credit_on_spending) +
				' VND'
			);
		},
		creditAmountInTeamCurrency() {
			return (
				this.$formatMoney(this.$account.feature_flags.referral_income) + ' VND'
			);
		}
	}
};
</script>
