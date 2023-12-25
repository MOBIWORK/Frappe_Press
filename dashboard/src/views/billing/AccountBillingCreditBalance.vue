<template>
	<Card title="Số dư tiền nạp" subtitle="Lịch sử số dư tiền nạp của bạn">
		<div class="max-h-96 divide-y">
			<div
				class="grid grid-cols-6 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-6"
			>
				<span class="hidden md:inline">Ngày</span>
				<span class="col-span-2 md:col-span-1">Mô tả</span>
				<span>Số tiền</span>
				<span>Số dư</span>
				<span>Trạng thái</span>
				<span></span>
			</div>
			<div
				class="grid grid-cols-6 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-6"
				v-for="d in dataTrans"
				:key="d.name"
			>
				<div class="hidden md:block">
					{{ formatDate(d) }}
				</div>
				<div class="col-span-2 whitespace-nowrap text-gray-700 md:col-span-1">
					<div>
						{{ getDescription(d) }}
					</div>
					<div class="md:hidden">{{ formatDate(d) }}</div>
				</div>
				<div class="whitespace-nowrap text-gray-700">
					{{ d.formatted.amount }}
				</div>
				<div class="whitespace-nowrap">{{ d.formatted.ending_balance }}</div>
				<div>
					<StatusOrder
						:status="getStatus(d)"
						:description="statusDoc[getStatus(d)]"
					></StatusOrder>
				</div>
				<div
					class="flex min-w-40 space-x-2"
					v-if="
						d.docstatus == 0 &&
						d.payos_payment_status == 'PENDING' &&
						d.checkout_url
					"
				>
					<Link :href="d.checkout_url" class="border-none">
						<Button
							:variant="'solid'"
							theme="blue"
							size="sm"
							label="Button"
							:loading="false"
							:loadingText="null"
							:disabled="false"
							:link="null"
						>
							Thanh toán
						</Button>
					</Link>
					<div>
						<Button
							:variant="'solid'"
							theme="red"
							size="sm"
							label="Button"
							@click="$resources.cancelOrder.submit({ name: d.name })"
							:loading="$resources.cancelOrder.loading"
						>
							Hủy
						</Button>
					</div>
				</div>
			</div>
		</div>
	</Card>
</template>
<script>
import { notify } from '@/utils/toast';
import StatusOrder from '@/components/StatusOrder.vue';

export default {
	name: 'AccountBillingCreditBalance',
	data() {
		return {
			dataTrans: [],
			statusDoc: {
				0: 'Chờ thanh toán',
				1: 'Đã thanh toán',
				2: 'Đã hủy',
				3: 'Chờ xử lý'
			}
		};
	},
	resources: {
		balances() {
			return {
				url: 'press.api.billing.balances',
				auto: true,
				onSuccess(data) {
					this.dataTrans = data;
				}
			};
		},
		payosReturnCancelOrder() {
			var query = this.$route.query;
			if (
				query.id &&
				query.orderCode &&
				query.cancel == 'true' &&
				query.code == '00' &&
				query.status == 'CANCELLED'
			) {
				return {
					url: 'press.api.billing.payos_return_cancel_order',
					params: {
						order_code: query.orderCode
					},
					auto: true,
					onSuccess(data) {
						this.$resources.balances.submit();
					}
				};
			}
		},
		cancelOrder() {
			return {
				url: 'press.api.billing.cancel_order',
				async onSuccess(data) {
					if (data.code == '00') {
						this.$resources.balances.submit();
					} else {
						notify({
							title: data.desc,
							color: 'red',
							icon: 'x'
						});
					}
				},
				onError(e) {
					notify({
						title: 'Có lỗi xảy ra vui lòng thử lại.',
						color: 'red',
						icon: 'x'
					});
				}
			};
		}
	},
	methods: {
		getStatus(d) {
			var statusCode = 3;
			if (d.docstatus == 1) {
				statusCode = 1;
			} else if (d.payos_payment_status == 'CANCELLED' || d.docstatus == 2) {
				statusCode = 2;
			} else if (d.payos_payment_status == 'PENDING' && d.docstatus == 0) {
				statusCode = 0;
			}
			return statusCode;
		},
		formatDate(d) {
			return this.$date(d.creation).toFormat('dd-MM-yyyy');
		},
		getDescription(d) {
			var typeSource = {
				'Prepaid Credits': 'Trả trước',
				'Transferred Credits': 'Tiền nạp',
				'Free Credits': 'Tiền ưu đãi'
			};

			if (d.type === 'Applied To Invoice' && d.formatted.invoice_for) {
				return `Hóa đơn cho ${d.formatted.invoice_for}`;
			}

			return d.amount < 0 ? d.type : typeSource[d.source];
		}
	}
};
</script>
