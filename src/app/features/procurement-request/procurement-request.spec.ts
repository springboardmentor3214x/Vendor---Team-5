import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementRequest } from './procurement-request';

describe('ProcurementRequest', () => {
  let component: ProcurementRequest;
  let fixture: ComponentFixture<ProcurementRequest>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementRequest],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementRequest);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
