<template>
	<Card
		v-if="referralLink"
		title="Giới thiệu và kiếm tiền"
		subtitle="Liên kết giới thiệu duy nhất của bạn"
	>
		<div class="space-y-4">
			<ClickToCopyField :textContent="referralLink" />
			<h3 class="text-base text-gray-700">
				Khi ai đó đăng ký bằng liên kết trên và chi ít nhất
				{{ minimumSpentAmount }} cho MBW Cloud, Bạn
				<strong
					>nhận được {{ creditAmountInTeamCurrency }} trong tín dụng MBW
					Cloud</strong
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
