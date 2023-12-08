<template>
	<Card title="Phương thức thanh toán" :subtitle="subtitle">
		<template #actions>
			<Button @click="showAddCardDialog = true"> Thêm thẻ </Button>
			<Dialog :options="{ title: 'Thêm thẻ mới' }" v-model="showAddCardDialog">
				<template v-slot:body-content>
					<StripeCard
						class="mb-1"
						v-if="showAddCardDialog"
						@complete="
							showAddCardDialog = false;
							$resources.paymentMethods.reload();
						"
					/>
				</template>
			</Dialog>
		</template>
		<div class="space-y-3">
			<div
				class="flex items-center justify-between rounded-lg border p-5"
				v-for="card in $resources.paymentMethods.data"
				:key="card.name"
			>
				<div class="flex">
					<component
						class="mr-6 h-12 w-12"
						:is="cardBrand[card.brand]"
						v-if="card.brand"
					/>
					<component class="mr-6 h-12 w-12" :is="cardBrand['generic']" v-else />
					<div class="my-auto">
						<div class="text-lg font-medium text-gray-900">
							{{ card.name_on_card }} <span class="text-gray-500">••••</span>
							{{ card.last_4 }}
							<Badge v-if="card.is_default" label="Default" />
						</div>
						<div class="mt-1 text-sm text-gray-600">
							<span>
								Hiệu lực đến {{ card.expiry_month }}/{{ card.expiry_year }}
							</span>
							·
							<span
								>Đã thêm vào {{ $date(card.creation).toLocaleString() }}</span
							>
						</div>
					</div>
				</div>
				<Dropdown :options="dropdownItems(card)" right>
					<template v-slot="{ open }">
						<Button icon="more-horizontal" />
					</template>
				</Dropdown>
			</div>
		</div>
	</Card>
	<FinalizeInvoicesDialog v-model="showFinalizeDialog" />
</template>

<script>
import { defineAsyncComponent } from 'vue';
import FinalizeInvoicesDialog from './FinalizeInvoicesDialog.vue';

export default {
	name: 'AccountBillingCards',
	data() {
		return {
			showAddCardDialog: false,
			showFinalizeDialog: false
		};
	},
	resources: {
		paymentMethods: {
			url: 'press.api.billing.get_payment_methods',
			auto: true
		},
		setAsDefault: {
			url: 'press.api.billing.set_as_default'
		},
		remove() {
			return {
				url: 'press.api.billing.remove_payment_method',
				onSuccess: data => {
					if (data === 'Unpaid Invoices') {
						this.showFinalizeDialog = true;
					}
				}
			};
		}
	},
	components: {
		StripeCard: defineAsyncComponent(() =>
			import('@/components/StripeCard.vue')
		),
		FinalizeInvoicesDialog
	},
	computed: {
		subtitle() {
			if (
				this.$resources.paymentMethods.loading ||
				this.$resources.paymentMethods.data?.length > 0
			) {
				return 'Các thẻ của bạn đã thêm để thanh toán tự động';
			}
			return 'Bạn chưa thêm bất kỳ thẻ nào cho việc thanh toán tự động';
		},
		cardBrand() {
			return {
				'master-card': defineAsyncComponent(() =>
					import('@/components/icons/cards/MasterCard.vue')
				),
				visa: defineAsyncComponent(() =>
					import('@/components/icons/cards/Visa.vue')
				),
				amex: defineAsyncComponent(() =>
					import('@/components/icons/cards/Amex.vue')
				),
				jcb: defineAsyncComponent(() =>
					import('@/components/icons/cards/JCB.vue')
				),
				generic: defineAsyncComponent(() =>
					import('@/components/icons/cards/Generic.vue')
				),
				'union-pay': defineAsyncComponent(() =>
					import('@/components/icons/cards/UnionPay.vue')
				)
			};
		}
	},
	methods: {
		dropdownItems(card) {
			return [
				!card.is_default && {
					label: 'Đặt mặc định',
					onClick: () => this.confirmSetAsDefault(card)
				},
				{
					label: 'Xóa',
					onClick: () => this.confirmRemove(card)
				}
			];
		},
		confirmSetAsDefault(card) {
			this.$confirm({
				title: 'Đặt mặc định',
				message: 'Đặt thẻ này làm phương thức thanh toán mặc định?',
				actionLabel: 'Đặt mặc định',
				resource: this.$resources.setAsDefault,
				action: closeDialog => {
					this.$resources.setAsDefault.submit({ name: card.name }).then(() => {
						this.$resources.paymentMethods.reload();
						closeDialog();
					});
				}
			});
		},
		confirmRemove(card) {
			this.$confirm({
				title: 'Xóa phương thức thanh toán',
				message: 'Bạn có chắc chắn muốn xóa phương thức thanh toán này không?',
				actionLabel: 'Xóa',
				actionColor: 'red',
				resource: this.$resources.remove,
				action: closeDialog => {
					this.$resources.remove.submit({ name: card.name }).then(() => {
						this.$resources.paymentMethods.reload();
						closeDialog();
					});
				}
			});
		}
	}
};
</script>
